package com.gramsense.persistence.entity;

import com.gramsense.persistence.entity.enumeration.GrammarLevel;
import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */

@Getter
@Setter
@Entity
@Table(name = "examples")
public class Example {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "grammar_topic", nullable = false, length = 50)
    @Enumerated(EnumType.STRING)
    private GrammarTopic grammarTopic;

    @Column(name = "grammar_level", nullable = false, length = 25)
    @Enumerated(EnumType.STRING)
    private GrammarLevel grammarLevel;

    @Column(name = "sentence", nullable = false, columnDefinition = "TEXT")
    private String sentence;

    @Column(name = "explanation", columnDefinition = "TEXT")
    private String explanation;

    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
}
