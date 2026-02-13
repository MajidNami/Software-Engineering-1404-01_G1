package com.gramsense.api.model.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Getter
@Setter
public class ExerciseAnswerResponse {

    private long exerciseId;
    @JsonProperty("isCorrect")
    private boolean isCorrect;
    private String correctAnswer;
}
