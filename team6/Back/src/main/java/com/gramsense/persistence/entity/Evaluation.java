package com.gramsense.persistence.entity;

import com.gramsense.persistence.entity.enumeration.EvaluationType;
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
@Table(name = "evaluations")
public class Evaluation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "grammar_user_id", nullable = false)
    private GrammarUser grammarUser;

    @Column(name = "grammar_topic", length = 50)
    @Enumerated(EnumType.STRING)
    private GrammarTopic grammarTopic;

    @Column(name = "detected_grammar_level", length = 25)
    @Enumerated(EnumType.STRING)
    private GrammarLevel detectedGrammarLevel;

    @Column(name = "evaluation_type", nullable = false, length = 10)
    @Enumerated(EnumType.STRING)
    private EvaluationType evaluationType;

    @Column(name = "original_sentence", nullable = false, columnDefinition = "TEXT")
    private String originalSentence;

    @Column(name = "corrected_sentence", columnDefinition = "TEXT")
    private String correctedSentence;

    @Column(name = "is_correct", nullable = false)
    private boolean isCorrect;

    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
}
