package com.gramsense.api.service;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.time.Instant;
import java.util.Date;
import java.util.Map;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Component
public class JwtService {

    @Value("${gramsense.auth.secret-key}")
    private final String SECRET_KEY;

    @Value("${gramsense.auth.expiration-seconds}")
    private final long EXPIRATION_SECONDS;

    private final SecretKey key;

    public JwtService (@Value("${gramsense.auth.secret-key}") String secretKey,
                       @Value("${gramsense.auth.expiration-seconds}")long expirationSeconds) {
        this.SECRET_KEY = secretKey;
        this.EXPIRATION_SECONDS = expirationSeconds;
        this.key = Keys.hmacShaKeyFor(SECRET_KEY.getBytes());
    }

    public String generateToken(Map<String, Object> claims) {
        Instant now = Instant.now();
        return Jwts.builder().claims(claims)
                .issuedAt(Date.from(now))
                .expiration(Date.from(now.plusSeconds(EXPIRATION_SECONDS)))
                .signWith(key, Jwts.SIG.HS256)
                .compact();
    }

    public Map<String, Object> validateAndGetClaims(String token) {
        return Jwts.parser()
                .verifyWith(key)
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}
