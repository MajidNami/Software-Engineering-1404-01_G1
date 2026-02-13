package com.gramsense.api.model.response;

import com.gramsense.persistence.entity.enumeration.GrammarLevel;
import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import lombok.Getter;
import lombok.Setter;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Getter
@Setter
public class UserStatsResponseDto {

    private GrammarTopic grammarTopic;
    private GrammarLevel grammarLevel;
    private int sentEvaluations;
    private int correctEvaluations;
    private int seenExamples;
    private int attemptedExercises;
    private int correctExercises;
}
