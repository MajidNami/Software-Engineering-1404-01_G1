package com.gramsense.api.model;

import lombok.Getter;
import lombok.Setter;
import org.springframework.stereotype.Component;
import org.springframework.web.context.annotation.RequestScope;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Getter
@Setter
@RequestScope
@Component
public class RequestContext {

    private Long userId;
}
