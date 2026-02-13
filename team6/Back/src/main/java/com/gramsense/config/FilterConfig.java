package com.gramsense.config;

import com.gramsense.api.filter.AuthFilter;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Configuration
public class FilterConfig {

    @Bean
    public FilterRegistrationBean<AuthFilter> jwtAuthFilterRegistration(AuthFilter filter) {
        FilterRegistrationBean<AuthFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(filter);
        registration.addUrlPatterns("/*");
        registration.setOrder(1);
        return registration;
    }
}
