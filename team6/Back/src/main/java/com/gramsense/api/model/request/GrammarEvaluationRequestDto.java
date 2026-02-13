package com.gramsense.api.model.request;

import com.gramsense.persistence.entity.enumeration.EvaluationType;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Getter
@Setter
public class GrammarEvaluationRequestDto {

    @NotNull
    private String sentence;
    @NotNull
    private EvaluationType evaluationType;
}
