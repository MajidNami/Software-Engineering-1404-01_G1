package com.gramsense.api.service;

import com.gramsense.api.model.DtoAssembler;
import com.gramsense.api.model.RequestContext;
import com.gramsense.api.model.request.GrammarEvaluationRequestDto;
import com.gramsense.api.model.response.EvaluationDetailDto;
import com.gramsense.api.model.response.GrammarEvaluationResponseDto;
import com.gramsense.persistence.entity.Evaluation;
import com.gramsense.persistence.entity.Example;
import com.gramsense.persistence.entity.Exercise;
import com.gramsense.persistence.entity.GrammarUser;
import com.gramsense.persistence.entity.UserStats;
import com.gramsense.persistence.entity.enumeration.GrammarLevel;
import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import com.gramsense.persistence.repository.EvaluationRepository;
import com.gramsense.persistence.repository.ExampleRepository;
import com.gramsense.persistence.repository.ExerciseRepository;
import com.gramsense.persistence.repository.GrammarUserRepository;
import com.gramsense.persistence.repository.UserStatsRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

@Service
@RequiredArgsConstructor
public class GrammarEvaluationServiceImpl implements GrammarEvaluationService {

    private final ExampleRepository exampleRepository;
    private final ExerciseRepository exerciseRepository;
    private final EvaluationRepository evaluationRepository;
    private final GrammarUserRepository grammarUserRepository;
    private final UserStatsRepository userStatsRepository;
    private final RequestContext requestContext;
    private final DtoAssembler dtoAssembler;

    /**
     * Simple rule-based grammar rules for common English errors.
     * Each rule maps a regex pattern to a grammar topic.
     */
    private static final List<GrammarRule> GRAMMAR_RULES = List.of(
            // Subject-verb agreement — third person singular present simple
            new GrammarRule(
                    Pattern.compile("\\b(he|she|it)\\s+(go|do|have|come|make|take|run|eat|drink|play|work|live|study|write|read|speak|want|need|like|try|start|begin|help|ask|teach|learn)\\b", Pattern.CASE_INSENSITIVE),
                    GrammarTopic.PRESENT_SIMPLE,
                    "Third person singular requires the verb to end with -s/-es"
            ),
            // "a" before vowel sound → should be "an"
            new GrammarRule(
                    Pattern.compile("\\ba\\s+[aeiou]\\w+", Pattern.CASE_INSENSITIVE),
                    GrammarTopic.ARTICLES,
                    "Use 'an' before words starting with a vowel sound"
            ),
            // "did" + past tense verb → should be base form
            new GrammarRule(
                    Pattern.compile("\\bdid\\s+(went|came|saw|ate|drank|ran|wrote|spoke|sang|swam|drove|flew|bought|sold|gave|sent|told|said|knew|thought|felt|heard)\\b", Pattern.CASE_INSENSITIVE),
                    GrammarTopic.PAST_SIMPLE,
                    "After 'did', use the base form of the verb"
            ),
            // "more" + comparative adjective ending in -er
            new GrammarRule(
                    Pattern.compile("\\bmore\\s+(bigger|smaller|faster|slower|taller|shorter|older|younger|easier|harder|simpler|nicer|cheaper)\\b", Pattern.CASE_INSENSITIVE),
                    GrammarTopic.COMPARISON,
                    "Do not use 'more' with adjectives that already have a comparative -er form"
            ),
            // "if I was" → should be "if I were" (second conditional)
            new GrammarRule(
                    Pattern.compile("\\bif\\s+I\\s+was\\b", Pattern.CASE_INSENSITIVE),
                    GrammarTopic.CONDITIONAL_SECOND,
                    "Use 'were' instead of 'was' in hypothetical conditions"
            ),
            // Present perfect with specific past time ("have/has ... yesterday/last week")
            new GrammarRule(
                    Pattern.compile("\\b(have|has)\\s+\\w+\\s+.*\\b(yesterday|last\\s+(week|month|year|night))\\b", Pattern.CASE_INSENSITIVE),
                    GrammarTopic.PRESENT_PERFECT,
                    "Do not use present perfect with specific past time expressions"
            ),
            // Missing "be" before -ing verb (present continuous)
            new GrammarRule(
                    Pattern.compile("\\b(I|you|we|they|he|she|it)\\s+(?!am\\b|is\\b|are\\b|was\\b|were\\b|will\\b|would\\b|can\\b|could\\b|may\\b|might\\b|must\\b|have\\b|has\\b|had\\b|do\\b|does\\b|did\\b)[a-z]+ing\\b", Pattern.CASE_INSENSITIVE),
                    GrammarTopic.PRESENT_CONTINUOUS,
                    "Present continuous requires a form of 'be' (am/is/are) before the -ing verb"
            ),
            // Reported speech with present tense after "said"
            new GrammarRule(
                    Pattern.compile("\\bsaid\\s+that\\s+\\w+\\s+(is|are|am|have|has|do|does|will|can|may)\\b", Pattern.CASE_INSENSITIVE),
                    GrammarTopic.REPORTED_SPEECH,
                    "In reported speech after 'said', shift the tense back"
            )
    );

    private static final Map<String, String> PAST_TO_BASE = Map.ofEntries(
            Map.entry("went", "go"), Map.entry("came", "come"), Map.entry("saw", "see"),
            Map.entry("ate", "eat"), Map.entry("drank", "drink"), Map.entry("ran", "run"),
            Map.entry("wrote", "write"), Map.entry("spoke", "speak"), Map.entry("sang", "sing"),
            Map.entry("swam", "swim"), Map.entry("drove", "drive"), Map.entry("flew", "fly"),
            Map.entry("bought", "buy"), Map.entry("sold", "sell"), Map.entry("gave", "give"),
            Map.entry("sent", "send"), Map.entry("told", "tell"), Map.entry("said", "say"),
            Map.entry("knew", "know"), Map.entry("thought", "think"), Map.entry("felt", "feel"),
            Map.entry("heard", "hear")
    );

    @Override
    @Transactional
    public GrammarEvaluationResponseDto evaluateGrammar(GrammarEvaluationRequestDto requestDto) {
        String sentence = requestDto.getSentence();
        Long userId = requestContext.getUserId();
        GrammarUser user = grammarUserRepository.getReferenceById(userId);

        GrammarEvaluationResponseDto response = new GrammarEvaluationResponseDto();

        // Detect grammar errors using rule-based matching
        GrammarTopic detectedTopic = null;
        String correctedSentence = sentence;
        boolean isCorrect = true;

        for (GrammarRule rule : GRAMMAR_RULES) {
            if (rule.pattern().matcher(sentence).find()) {
                detectedTopic = rule.topic();
                isCorrect = false;
                correctedSentence = applyCorrection(sentence, rule);
                break;
            }
        }

        // If no error detected, determine topic from sentence context
        if (detectedTopic == null) {
            detectedTopic = detectTopicFromContent(sentence);
        }

        response.setCorrect(isCorrect);

        if (!isCorrect) {
            EvaluationDetailDto detail = new EvaluationDetailDto();
            detail.setOriginal(sentence);
            detail.setCorrected(correctedSentence);
            detail.setGrammarTopic(detectedTopic);
            response.setEvaluation(detail);

            // Fetch related examples and exercises from DB (business rule: 1 each at MEDIUM level)
            List<Example> examples = exampleRepository.findFreshExamples(userId, detectedTopic, GrammarLevel.MEDIUM);
            List<Exercise> exercises = exerciseRepository.findFreshExercises(userId, detectedTopic, GrammarLevel.MEDIUM);

            response.setExamples(dtoAssembler.toExampleDtoList(examples));
            response.setExercises(dtoAssembler.toExerciseDtoList(exercises));
        } else {
            response.setExamples(Collections.emptyList());
            response.setExercises(Collections.emptyList());
        }

        // Persist evaluation
        Evaluation evaluation = new Evaluation();
        evaluation.setGrammarUser(user);
        evaluation.setGrammarTopic(detectedTopic);
        evaluation.setDetectedGrammarLevel(GrammarLevel.MEDIUM);
        evaluation.setEvaluationType(requestDto.getEvaluationType());
        evaluation.setOriginalSentence(sentence);
        evaluation.setCorrectedSentence(isCorrect ? null : correctedSentence);
        evaluation.setCorrect(isCorrect);
        evaluationRepository.save(evaluation);

        // Update user stats
        GrammarTopic finalDetectedTopic = detectedTopic;
        UserStats userStats = userStatsRepository
                .findByGrammarUserIdAndGrammarTopicAndGrammarLevel(userId, detectedTopic, GrammarLevel.MEDIUM)
                .orElseGet(() -> {
                    UserStats newStats = new UserStats();
                    newStats.setGrammarUser(user);
                    newStats.setGrammarTopic(finalDetectedTopic);
                    newStats.setGrammarLevel(GrammarLevel.MEDIUM);
                    return newStats;
                });

        userStats.setTotalSentEvaluations(userStats.getTotalSentEvaluations() + 1);
        if (isCorrect) {
            userStats.setTotalCorrectEvaluations(userStats.getTotalCorrectEvaluations() + 1);
        }
        userStats.setUpdatedAt(LocalDateTime.now());
        userStatsRepository.save(userStats);

        return response;
    }

    /**
     * Detect the grammar topic based on sentence content (keyword heuristics).
     * Used when no error is detected, to still categorize the sentence.
     */
    private GrammarTopic detectTopicFromContent(String sentence) {
        String lower = sentence.toLowerCase();
        if (lower.contains("if") && (lower.contains("would") || lower.contains("will")))
            return GrammarTopic.CONDITIONAL_FIRST;
        if (lower.contains("was") || lower.contains("were") || lower.contains("did") || lower.matches(".*\\b\\w+ed\\b.*"))
            return GrammarTopic.PAST_SIMPLE;
        if (lower.contains("have been") || lower.contains("has been"))
            return GrammarTopic.PRESENT_PERFECT;
        if (lower.contains("a ") || lower.contains("an ") || lower.contains("the "))
            return GrammarTopic.ARTICLES;
        return GrammarTopic.PRESENT_SIMPLE;
    }

    /**
     * Apply a simple correction based on the matched grammar rule.
     */
    private String applyCorrection(String sentence, GrammarRule rule) {
        return switch (rule.topic()) {
            case PRESENT_SIMPLE -> rule.pattern().matcher(sentence).replaceFirst(match -> {
                String subject = match.group(1);
                String verb = match.group(2).toLowerCase();
                String conjugated;
                if ("go".equals(verb)) conjugated = "goes";
                else if ("do".equals(verb)) conjugated = "does";
                else if ("have".equals(verb)) conjugated = "has";
                else if (verb.endsWith("ch") || verb.endsWith("sh") || verb.endsWith("ss") || verb.endsWith("x") || verb.endsWith("o"))
                    conjugated = verb + "es";
                else if (verb.endsWith("y") && !"aeiou".contains(String.valueOf(verb.charAt(verb.length() - 2))))
                    conjugated = verb.substring(0, verb.length() - 1) + "ies";
                else conjugated = verb + "s";
                return subject + " " + conjugated;
            });
            case ARTICLES -> sentence.replaceAll("(?i)\\ba\\s+([aeiou])", "an $1");
            case PAST_SIMPLE -> {
                String result = sentence;
                for (Map.Entry<String, String> entry : PAST_TO_BASE.entrySet()) {
                    result = result.replaceAll("(?i)(did\\s+)" + Pattern.quote(entry.getKey()), "did " + entry.getValue());
                }
                yield result;
            }
            case CONDITIONAL_SECOND -> sentence.replaceAll("(?i)if I was", "if I were");
            case COMPARISON -> rule.pattern().matcher(sentence).replaceFirst(match -> match.group(1));
            default -> sentence;
        };
    }

    private record GrammarRule(Pattern pattern, GrammarTopic topic, String description) {}
}
