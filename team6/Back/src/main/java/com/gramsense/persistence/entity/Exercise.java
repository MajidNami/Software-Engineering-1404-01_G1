package com.gramsense.persistence.entity;

import com.gramsense.persistence.entity.enumeration.ExerciseType;
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
@Table(name = "exercises")
public class Exercise {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "grammar_topic", nullable = false, length = 50)
    @Enumerated(EnumType.STRING)
    private GrammarTopic grammarTopic;

    @Column(name = "exercise_type", nullable = false, length = 25)
    @Enumerated(EnumType.STRING)
    private ExerciseType exerciseType;

    @Column(name = "grammar_level", nullable = false, length = 25)
    @Enumerated(EnumType.STRING)
    private GrammarLevel grammarLevel;

    @Column(name = "question", nullable = false, columnDefinition = "TEXT")
    private String question;

    @Column(name = "correct_answer", nullable = false, columnDefinition = "TEXT")
    private String correctAnswer;

    @Column(name = "options", columnDefinition = "TEXT")
    private String options;

    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
}
