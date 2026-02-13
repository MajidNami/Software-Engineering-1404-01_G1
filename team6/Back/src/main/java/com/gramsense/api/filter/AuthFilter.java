package com.gramsense.api.filter;

import com.gramsense.api.model.RequestContext;
import com.gramsense.api.service.JwtService;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Map;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Component
@RequiredArgsConstructor
public class AuthFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final RequestContext requestContext;

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String uri = request.getRequestURI();
        String method = request.getMethod();
        return "/api/users/login".equals(uri)
                || "/api/users/register".equals(uri)
                || "OPTIONS".equalsIgnoreCase(method);
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }

        String token = authHeader.substring("Bearer ".length());
        Map<String, Object> claims;
        try {
            claims = jwtService.validateAndGetClaims(token);
        } catch (Exception e) {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }

        Object userIdRaw = claims.get("userId");
        if (userIdRaw == null) {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }

        long userId;
        if (userIdRaw instanceof Number) {
            userId = ((Number) userIdRaw).longValue();
        } else {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }

        requestContext.setUserId(userId);
        filterChain.doFilter(request, response);
    }
}
