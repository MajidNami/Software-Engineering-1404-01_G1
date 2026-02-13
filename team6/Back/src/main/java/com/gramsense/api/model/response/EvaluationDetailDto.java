package com.gramsense.api.model.response;

import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import lombok.Getter;
import lombok.Setter;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Getter
@Setter
public class EvaluationDetailDto {

    private String original;
    private String corrected;
    private GrammarTopic grammarTopic;
}
