import React from 'react'
import { Navigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext.jsx'
import HomePage from '../../pages/public/HomePage.jsx'

/**
 * LandingRoute determines whether to show the citizen-facing public homepage
 * or redirect an authenticated administrative or student user to their role-specific dashboard.
 *
 * Rules:
 * - Unauthenticated visitors -> Citizen Public Homepage.
 * - Citizen / Parent -> Citizen Public Homepage (they explore institutions & access portal via header).
 * - Platform Administrator (`platform_admin`) -> Central Governance & Monitoring Dashboard (`/admin`).
 * - Institution Administrator (`school_admin`, `academic_admin`, `institution_admin`) -> Institution Dashboard (`/institution-admin`).
 * - Institution Staff (`school_staff`, `admissions_officer`, `student_records_officer`, etc.) -> Staff Dashboard (`/staff`).
 * - Student (`student`) -> Student Dashboard (`/student`).
 *
 * If an authenticated user explicitly wants to view the public portal (e.g. `/?view=public`),
 * the public homepage is rendered without redirecting them, preventing navigation loops.
 */
export default function LandingRoute() {
  const { isAuthenticated, user, loading } = useAuth()
  const [searchParams] = useSearchParams()

  // If auth is still verifying stored token on mount, render nothing or lightweight placeholder
  if (loading) {
    return null
  }

  // If visitor is not authenticated, show public homepage
  if (!isAuthenticated || !user) {
    return <HomePage />
  }

  // If explicitly requested to view the public homepage (avoids redirection loops)
  if (searchParams.get('view') === 'public') {
    return <HomePage />
  }

  const role = user.role

  switch (role) {
    case 'platform_admin':
      return <Navigate to="/admin" replace />

    case 'school_admin':
    case 'institution_admin':
      return <Navigate to="/institution-admin" replace />

    case 'school_staff':
    case 'admissions_officer':
    case 'academic_admin':
    case 'student_records_officer':
    case 'general_staff':
      return <Navigate to="/staff" replace />

    case 'student':
      return <Navigate to="/student" replace />

    case 'parent':
    default:
      // Citizens and parents stay on the public homepage as their primary discovery portal
      return <HomePage />
  }
}
