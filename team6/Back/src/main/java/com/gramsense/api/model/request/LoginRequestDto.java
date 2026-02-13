package com.gramsense.api.model.request;

import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Getter
@Setter
public class LoginRequestDto {

    @NotNull
    private String username;
    @NotNull
    private String password;
}
