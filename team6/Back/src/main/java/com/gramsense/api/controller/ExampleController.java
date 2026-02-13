package com.gramsense.api.controller;

import com.gramsense.api.model.DtoAssembler;
import com.gramsense.api.model.RequestContext;
import com.gramsense.api.model.response.ExampleResponseDto;
import com.gramsense.persistence.entity.Example;
import com.gramsense.persistence.entity.GrammarUser;
import com.gramsense.persistence.entity.UserExampleHistory;
import com.gramsense.persistence.entity.UserStats;
import com.gramsense.persistence.entity.enumeration.GrammarLevel;
import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import com.gramsense.persistence.repository.ExampleRepository;
import com.gramsense.persistence.repository.GrammarUserRepository;
import com.gramsense.persistence.repository.UserExampleHistoryRepository;
import com.gramsense.persistence.repository.UserStatsRepository;
import jakarta.validation.constraints.NotNull;
import lombok.RequiredArgsConstructor;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;
import java.util.List;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */

@RestController
@RequestMapping("/api/examples")
@RequiredArgsConstructor
public class ExampleController {

    private final ExampleRepository exampleRepository;
    private final UserExampleHistoryRepository exampleHistoryRepository;
    private final UserStatsRepository userStatsRepository;
    private final GrammarUserRepository grammarUserRepository;
    private final DtoAssembler dtoAssembler;
    private final RequestContext requestContext;

    @Transactional
    @GetMapping
    public ExampleResponseDto getExamples(@NotNull @RequestParam GrammarTopic grammarTopic, @NotNull @RequestParam GrammarLevel grammarLevel) {
        Long userId = requestContext.getUserId();
        GrammarUser user = grammarUserRepository.getReferenceById(userId);
        List<Example> examples = exampleRepository.findFreshExamples(userId, grammarTopic, grammarLevel);
        if (examples.isEmpty()) {
            return new ExampleResponseDto();
        }

        UserStats userStats = userStatsRepository.findByGrammarUserIdAndGrammarTopicAndGrammarLevel(userId, grammarTopic, grammarLevel)
                .orElseGet(() -> {
                    UserStats newStats = new UserStats();
                    newStats.setGrammarUser(user);
                    newStats.setGrammarTopic(grammarTopic);
                    newStats.setGrammarLevel(grammarLevel);
                    return newStats;
                });

        for (Example example : examples) {
            UserExampleHistory history = new UserExampleHistory();
            history.setGrammarUser(user);
            history.setExample(example);
            exampleHistoryRepository.save(history);

            userStats.setTotalSeenExamples(userStats.getTotalSeenExamples() + 1);
        }
        userStats.setUpdatedAt(LocalDateTime.now());
        userStatsRepository.save(userStats);

        return dtoAssembler.toExampleResponseDto(examples);
    }
}
