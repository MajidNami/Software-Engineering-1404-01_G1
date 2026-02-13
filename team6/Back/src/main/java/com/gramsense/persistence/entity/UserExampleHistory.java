package com.gramsense.persistence.entity;

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
@Table(name = "user_example_history")
public class UserExampleHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @ManyToOne(optional = false)
    @JoinColumn(name = "grammar_user_id", nullable = false)
    private GrammarUser grammarUser;

    @ManyToOne(optional = false)
    @JoinColumn(name = "example_id", nullable = false)
    private Example example;

    @CreationTimestamp
    @Column(name = "seen_at")
    private LocalDateTime seenAt;
}
