package com.gramsense.api.model;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gramsense.api.model.response.*;
import com.gramsense.persistence.entity.Example;
import com.gramsense.persistence.entity.Exercise;
import com.gramsense.persistence.entity.UserStats;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class DtoAssembler {

    private final ObjectMapper objectMapper;

    public ExampleResponseDto toExampleResponseDto(List<Example> examples) {
        ExampleResponseDto exampleResponseDto = new ExampleResponseDto();
        exampleResponseDto.setExamples(toExampleDtoList(examples));
        return exampleResponseDto;
    }

    public List<ExampleDto> toExampleDtoList(List<Example> examples) {
        List<ExampleDto> exampleDtoList = new ArrayList<>();
        for (Example example : examples) {
            ExampleDto exampleDto = new ExampleDto();
            exampleDto.setText(example.getSentence());
            exampleDto.setExplanation(example.getExplanation());
            exampleDtoList.add(exampleDto);
        }
        return exampleDtoList;
    }

    public ExerciseResponseDto toExerciseResponseDto(List<Exercise> exercises) {
        ExerciseResponseDto exerciseResponseDto = new ExerciseResponseDto();
        exerciseResponseDto.setExercises(toExerciseDtoList(exercises));
        return exerciseResponseDto;
    }

    public List<ExerciseDto> toExerciseDtoList(List<Exercise> exercises) {
        List<ExerciseDto> exerciseDtoList = new ArrayList<>();
        for (Exercise exercise : exercises) {
            ExerciseDto exerciseDto = new ExerciseDto();
            exerciseDto.setId(exercise.getId());
            exerciseDto.setGrammarTopic(exercise.getGrammarTopic());
            exerciseDto.setGrammarLevel(exercise.getGrammarLevel());
            exerciseDto.setExerciseType(exercise.getExerciseType());
            exerciseDto.setQuestion(exercise.getQuestion());
            List<String> optionsList = Collections.emptyList();
            try {
                if (StringUtils.hasText(exercise.getOptions())) {
                    optionsList = objectMapper.readValue(exercise.getOptions(), List.class);
                }
            } catch (JsonProcessingException e) {
                log.warn(e.getMessage(), e);
            }
            exerciseDto.setOptions(optionsList);
            exerciseDtoList.add(exerciseDto);
        }
        return exerciseDtoList;
    }

    public UserStatsResponseDto toUserStatsResponseDto(UserStats userStats) {
        UserStatsResponseDto userStatsResponseDto = new UserStatsResponseDto();
        if (userStats == null) {
            return userStatsResponseDto;
        }
        userStatsResponseDto.setGrammarTopic(userStats.getGrammarTopic());
        userStatsResponseDto.setGrammarLevel(userStats.getGrammarLevel());
        userStatsResponseDto.setSentEvaluations(userStats.getTotalSentEvaluations());
        userStatsResponseDto.setCorrectEvaluations(userStats.getTotalCorrectEvaluations());
        userStatsResponseDto.setSeenExamples(userStats.getTotalSeenExamples());
        userStatsResponseDto.setAttemptedExercises(userStats.getTotalAttemptedExercises());
        userStatsResponseDto.setCorrectExercises(userStats.getTotalCorrectExercises());
        return userStatsResponseDto;
    }
}
