package com.gramsense.persistence.entity;

import com.gramsense.persistence.entity.enumeration.GrammarLevel;
import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */

@Getter
@Setter
@Entity
@Table(name = "user_stats")
public class UserStats {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "grammar_user_id", nullable = false)
    private GrammarUser grammarUser;

    @Column(name = "grammar_topic", nullable = false, length = 50)
    @Enumerated(EnumType.STRING)
    private GrammarTopic grammarTopic;

    @Column(name = "grammar_level", nullable = false, length = 25)
    @Enumerated(EnumType.STRING)
    private GrammarLevel grammarLevel;

    @Column(name = "total_sent_evaluations")
    private int totalSentEvaluations;

    @Column(name = "total_correct_evaluations")
    private int totalCorrectEvaluations;

    @Column(name = "total_seen_examples")
    private int totalSeenExamples;

    @Column(name = "total_attempted_exercises")
    private int totalAttemptedExercises;

    @Column(name = "total_correct_exercises")
    private int totalCorrectExercises;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
