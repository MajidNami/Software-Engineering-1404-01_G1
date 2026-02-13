package com.gramsense.api.service;

import com.gramsense.api.model.request.GrammarEvaluationRequestDto;
import com.gramsense.api.model.response.GrammarEvaluationResponseDto;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
public interface GrammarEvaluationService {

    GrammarEvaluationResponseDto evaluateGrammar(GrammarEvaluationRequestDto requestDto);
}
