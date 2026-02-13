package com.gramsense.persistence.repository;

import com.gramsense.persistence.entity.Example;
import com.gramsense.persistence.entity.enumeration.GrammarLevel;
import com.gramsense.persistence.entity.enumeration.GrammarTopic;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Repository
public interface ExampleRepository extends JpaRepository<Example, Long> {

    @Query(value = "SELECT e FROM Example e " +
            "WHERE e.grammarTopic = :grammarTopic AND e.grammarLevel = :grammarLevel " +
            "AND e NOT IN (SELECT h.example FROM UserExampleHistory h WHERE h.grammarUser.id = :grammarUserId) " +
            "ORDER BY e.createdAt LIMIT 2")
    List<Example> findFreshExamples(Long grammarUserId, GrammarTopic grammarTopic, GrammarLevel grammarLevel);
}
