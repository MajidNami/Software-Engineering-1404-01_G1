package com.gramsense.api.controller;

import com.gramsense.api.model.DtoAssembler;
import com.gramsense.api.model.request.LoginRequestDto;
import com.gramsense.api.model.request.RegisterRequestDto;
import com.gramsense.api.model.response.ErrorResponseDto;
import com.gramsense.api.model.response.LoginResponseDto;
import com.gramsense.api.model.response.UserStatsResponseDto;
import com.gramsense.api.service.JwtService;
import com.gramsense.persistence.entity.GrammarUser;
import com.gramsense.persistence.entity.UserStats;
import com.gramsense.persistence.entity.enumeration.GrammarLevel;
import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import com.gramsense.persistence.repository.GrammarUserRepository;
import com.gramsense.persistence.repository.UserStatsRepository;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final GrammarUserRepository grammarUserRepository;
    private final UserStatsRepository userStatsRepository;
    private final JwtService jwtService;
    private final DtoAssembler dtoAssembler;

    @PostMapping(path = "/login")
    @Transactional(readOnly = true)
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequestDto requestDto) {
        GrammarUser user = grammarUserRepository.findByUsername(requestDto.getUsername()).orElse(null);
        if (user == null || !user.getPassword().equals(requestDto.getPassword())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(new ErrorResponseDto("Invalid username or password"));
        }
        String token = jwtService.generateToken(Map.of("userId", user.getId()));
        LoginResponseDto loginResponseDto = new LoginResponseDto();
        loginResponseDto.setToken(token);
        return ResponseEntity.ok(loginResponseDto);
    }

    @PostMapping(path = "/register")
    @Transactional
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequestDto requestDto) {
        if (grammarUserRepository.findByUsername(requestDto.getUsername()).isPresent()) {
            return ResponseEntity.badRequest()
                    .body(new ErrorResponseDto("Username already taken"));
        }

        GrammarUser user = new GrammarUser();
        user.setUsername(requestDto.getUsername());
        user.setPassword(requestDto.getPassword());
        user.setEmail(requestDto.getEmail());
        grammarUserRepository.save(user);

        String token = jwtService.generateToken(Map.of("userId", user.getId()));
        LoginResponseDto loginResponseDto = new LoginResponseDto();
        loginResponseDto.setToken(token);
        return ResponseEntity.status(HttpStatus.CREATED).body(loginResponseDto);
    }

    @GetMapping(path = "/{userId}/stats")
    @Transactional(readOnly = true)
    public UserStatsResponseDto getUserStats(@NotNull @PathVariable Long userId,
                                             @NotNull @RequestParam GrammarTopic grammarTopic,
                                             @NotNull @RequestParam GrammarLevel grammarLevel) {
        UserStats userStats = userStatsRepository
                .findByGrammarUserIdAndGrammarTopicAndGrammarLevel(userId, grammarTopic, grammarLevel)
                .orElse(null);
        return dtoAssembler.toUserStatsResponseDto(userStats);
    }

    @GetMapping(path = "/{userId}/stats/all")
    @Transactional(readOnly = true)
    public List<UserStatsResponseDto> getAllUserStats(@NotNull @PathVariable Long userId) {
        List<UserStats> statsList = userStatsRepository.findByGrammarUserId(userId);
        return statsList.stream().map(dtoAssembler::toUserStatsResponseDto).toList();
    }
}
