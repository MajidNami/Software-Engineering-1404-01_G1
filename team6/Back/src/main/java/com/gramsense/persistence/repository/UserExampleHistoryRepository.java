package com.gramsense.persistence.repository;

import com.gramsense.persistence.entity.UserExampleHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * @author Mehdi Kamali
 * @since 11/02/2026
 */
@Repository
public interface UserExampleHistoryRepository extends JpaRepository<UserExampleHistory, Long> {
}
