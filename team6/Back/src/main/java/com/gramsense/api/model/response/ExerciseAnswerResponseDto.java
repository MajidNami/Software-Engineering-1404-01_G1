package com.gramsense.api.model.response;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Getter
@Setter
public class ExerciseAnswerResponseDto {

    private List<ExerciseAnswerResponse> results;
}
