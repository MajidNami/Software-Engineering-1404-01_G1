package com.gramsense.api.controller;

import com.gramsense.api.model.DtoAssembler;
import com.gramsense.api.model.RequestContext;
import com.gramsense.api.model.request.ExerciseAnswerDto;
import com.gramsense.api.model.request.ExerciseAnswerRequestDto;
import com.gramsense.api.model.response.ExerciseAnswerResponse;
import com.gramsense.api.model.response.ExerciseAnswerResponseDto;
import com.gramsense.api.model.response.ExerciseResponseDto;
import com.gramsense.persistence.entity.Exercise;
import com.gramsense.persistence.entity.GrammarUser;
import com.gramsense.persistence.entity.UserExerciseHistory;
import com.gramsense.persistence.entity.UserStats;
import com.gramsense.persistence.entity.enumeration.GrammarLevel;
import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import com.gramsense.persistence.repository.ExerciseRepository;
import com.gramsense.persistence.repository.GrammarUserRepository;
import com.gramsense.persistence.repository.UserExerciseHistoryRepository;
import com.gramsense.persistence.repository.UserStatsRepository;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import lombok.RequiredArgsConstructor;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.CollectionUtils;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */

@RestController
@RequestMapping("/api/exercises")
@RequiredArgsConstructor
public class ExerciseController {

    private final ExerciseRepository exerciseRepository;
    private final UserExerciseHistoryRepository exerciseHistoryRepository;
    private final UserStatsRepository userStatsRepository;
    private final GrammarUserRepository grammarUserRepository;
    private final DtoAssembler dtoAssembler;
    private final RequestContext requestContext;

    @GetMapping
    @Transactional
    public ExerciseResponseDto getExercises(@NotNull @RequestParam GrammarTopic grammarTopic, @NotNull @RequestParam GrammarLevel grammarLevel) {
        Long userId = requestContext.getUserId();
        List<Exercise> exercises = exerciseRepository.findFreshExercises(userId, grammarTopic, grammarLevel);
        return dtoAssembler.toExerciseResponseDto(exercises);
    }

    @PostMapping("/answer")
    @Transactional
    public ExerciseAnswerResponseDto submitAnswers(@Valid @RequestBody ExerciseAnswerRequestDto requestDto) {
        ExerciseAnswerResponseDto responseDto = new ExerciseAnswerResponseDto();
        List<ExerciseAnswerDto> answers = requestDto.getAnswers();
        if (CollectionUtils.isEmpty(answers)) {
            return responseDto;
        }

        List<ExerciseAnswerResponse> results = new ArrayList<>();
        Long userId = requestContext.getUserId();
        GrammarUser user = grammarUserRepository.getReferenceById(userId);
        for (ExerciseAnswerDto answer : answers) {
            Exercise exercise = exerciseRepository.findById(answer.getExerciseId())
                    .orElseThrow(() -> new RuntimeException("Exercise not found"));
            boolean isCorrect = exercise.getCorrectAnswer().trim().equalsIgnoreCase(answer.getAnswer().trim());

            UserExerciseHistory history = new UserExerciseHistory();
            history.setGrammarUser(user);
            history.setExercise(exercise);
            history.setUserAnswer(answer.getAnswer());
            history.setCorrect(isCorrect);
            exerciseHistoryRepository.save(history);

            UserStats userStats = userStatsRepository.findByGrammarUserIdAndGrammarTopicAndGrammarLevel(userId, exercise.getGrammarTopic(), exercise.getGrammarLevel())
                    .orElseGet(() -> {
                        UserStats newStats = new UserStats();
                        newStats.setGrammarUser(user);
                        newStats.setGrammarTopic(exercise.getGrammarTopic());
                        newStats.setGrammarLevel(exercise.getGrammarLevel());
                        return newStats;
                    });

            userStats.setTotalAttemptedExercises(userStats.getTotalAttemptedExercises() + 1);
            if (isCorrect) {
                userStats.setTotalCorrectExercises(userStats.getTotalCorrectExercises() + 1);
            }
            userStats.setUpdatedAt(LocalDateTime.now());
            userStatsRepository.save(userStats);

            ExerciseAnswerResponse result = new ExerciseAnswerResponse();
            result.setExerciseId(exercise.getId());
            result.setCorrect(isCorrect);
            result.setCorrectAnswer(exercise.getCorrectAnswer());
            results.add(result);
        }

        responseDto.setResults(results);
        return responseDto;
    }
}
