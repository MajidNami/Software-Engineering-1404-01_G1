package com.gramsense.api.controller;

import com.gramsense.api.model.request.GrammarEvaluationRequestDto;
import com.gramsense.api.model.response.GrammarEvaluationResponseDto;
import com.gramsense.api.service.GrammarEvaluationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@RestController
@RequestMapping("/api/grammar")
@RequiredArgsConstructor
public class GrammarController {

    private final GrammarEvaluationService grammarEvaluationService;

    @PostMapping(path = "/evaluate")
    public GrammarEvaluationResponseDto evaluateGrammar(@Valid @RequestBody GrammarEvaluationRequestDto requestDto) {
        return grammarEvaluationService.evaluateGrammar(requestDto);
    }
}
