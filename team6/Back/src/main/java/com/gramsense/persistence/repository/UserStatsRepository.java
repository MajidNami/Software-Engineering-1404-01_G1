package com.gramsense.persistence.repository;

import com.gramsense.persistence.entity.UserStats;
import com.gramsense.persistence.entity.enumeration.GrammarLevel;
import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Repository
public interface UserStatsRepository extends JpaRepository<UserStats, Long> {

    Optional<UserStats> findByGrammarUserIdAndGrammarTopicAndGrammarLevel(Long grammarUserId, GrammarTopic grammarTopic, GrammarLevel grammarLevel);

    List<UserStats> findByGrammarUserId(Long grammarUserId);
}
