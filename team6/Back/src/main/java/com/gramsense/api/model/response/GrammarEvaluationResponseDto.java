package com.gramsense.api.model.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Getter
@Setter
public class GrammarEvaluationResponseDto {

    @JsonProperty("isCorrect")
    private boolean isCorrect;
    private EvaluationDetailDto evaluation;
    private List<ExampleDto> examples;
    private List<ExerciseDto> exercises;
}
