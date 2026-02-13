package com.gramsense.api.model.response;

import com.gramsense.persistence.entity.enumeration.ExerciseType;
import com.gramsense.persistence.entity.enumeration.GrammarLevel;
import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Getter
@Setter
public class ExerciseDto {

    private Long id;
    private GrammarTopic grammarTopic;
    private GrammarLevel grammarLevel;
    private ExerciseType exerciseType;
    private String question;
    private List<String> options;
}
