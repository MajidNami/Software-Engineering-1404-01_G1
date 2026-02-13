package com.gramsense.api.model.request;

import jakarta.validation.Valid;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Getter
@Setter
public class ExerciseAnswerRequestDto {

    @Valid
    private List<ExerciseAnswerDto> answers;
}
