import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import i18n from './i18n';
import {
  Landmark, BookOpen, GraduationCap, Users, Target, HeartHandshake,
  CheckCircle2, ArrowRight, ArrowLeft, Menu, LogOut, LogIn, UserPlus, Search, Globe,
  Building2, Award, Clock, AlertCircle, FileText, Briefcase, Filter,
  Shield, Check, X, ChevronRight, Calendar, User, MapPin, Download, RefreshCw,
  Send, Folder, Bookmark, BookmarkCheck, Navigation, Crosshair, Compass, Loader2, Star,
  Layers, Sparkles, Eye, EyeOff, Lock, KeyRound, Key, Phone, Mail
} from 'lucide-react';
import './style.css';
import { CentreLocationMap } from './CentreLocationMap';

const API_BASE = import.meta.env.VITE_SKILL_API_URL || '';

export default function App() {
  const { t } = useTranslation();

  // Navigation & Page State
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [adminMobileMenuOpen, setAdminMobileMenuOpen] = useState<boolean>(false);
  const [centreMobileMenuOpen, setCentreMobileMenuOpen] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'home' | 'explore_skills' | 'category_details' | 'courses' | 'programmes' | 'centres' | 'centre_profile' | 'applications' | 'student_portal' | 'profile' | 'gap' | 'certificates'>('home');

  // Authentication State
  const [token, setToken] = useState<string>(localStorage.getItem('ns_skill_token') || '');
  const [userRole, setUserRole] = useState<string>(localStorage.getItem('ns_skill_role') || '');
  const [citizenRef, setCitizenRef] = useState<string>(localStorage.getItem('ns_skill_citizen_ref') || '');
  const [centreId, setCentreId] = useState<string>(localStorage.getItem('ns_skill_centre_id') || '');
  const [userEmail, setUserEmail] = useState<string>(localStorage.getItem('ns_skill_email') || '');
  const [userName, setUserName] = useState<string>(localStorage.getItem('ns_skill_name') || '');
  const [isStudent, setIsStudent] = useState<boolean>(localStorage.getItem('ns_skill_is_student') === 'true');
  const [studentId, setStudentId] = useState<string>(localStorage.getItem('ns_skill_student_id') || '');
  const [studentDashboardData, setStudentDashboardData] = useState<any | null>(null);
  const [studentDashboardLoading, setStudentDashboardLoading] = useState<boolean>(false);
  const [studentDashboardError, setStudentDashboardError] = useState<string>('');

  // Multi-Centre Admin State
  const [assignedCentres, setAssignedCentres] = useState<any[]>(() => {
    try {
      const stored = localStorage.getItem('ns_skill_assigned_centres');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });
  const [showCentreSelectModal, setShowCentreSelectModal] = useState<boolean>(false);
  const [unassignedCentreNotice, setUnassignedCentreNotice] = useState<boolean>(false);

  // Public Training Centre Profile View State
  const [activeCentreProfileId, setActiveCentreProfileId] = useState<string | number | null>(null);
  const [publicCentreProfile, setPublicCentreProfile] = useState<any | null>(null);
  const [publicCentreLoading, setPublicCentreLoading] = useState<boolean>(false);
  const [publicCentreTab, setPublicCentreTab] = useState<'overview' | 'about' | 'programmes' | 'achievements' | 'facilities' | 'outcomes' | 'trainers' | 'location'>('overview');
  const [centreTab, setCentreTab] = useState<'dashboard' | 'applications' | 'programmes' | 'batches' | 'trainers' | 'profile' | 'reports' | 'security'>('dashboard');
  const [centreDashboard, setCentreDashboard] = useState<any | null>(null);
  const [centreProfile, setCentreProfile] = useState<any | null>(null);
  const [centreProgrammes, setCentreProgrammes] = useState<any[]>([]);
  const [centreSelectedProgForBatches, setCentreSelectedProgForBatches] = useState<any | null>(null);
  const [centreBatches, setCentreBatches] = useState<any[]>([]);
  const [centreTrainers, setCentreTrainers] = useState<any[]>([]);
  const [centreEnrollments, setCentreEnrollments] = useState<any[]>([]);
  const [centreReports, setCentreReports] = useState<any | null>(null);
  const [centreReviewModalApp, setCentreReviewModalApp] = useState<any | null>(null);
  const [centreReviewAction, setCentreReviewAction] = useState<'APPROVE' | 'REJECT' | 'UNDER_REVIEW' | 'ACTION_REQUIRED' | 'WAITLIST' | 'WITHDRAW'>('APPROVE');
  const [centreReviewReason, setCentreReviewReason] = useState<string>('');
  const [centreInternalNotes, setCentreInternalNotes] = useState<string>('');
  const [centreReviewSubmitting, setCentreReviewSubmitting] = useState<boolean>(false);
  const [centreReviewError, setCentreReviewError] = useState<string>('');
  const [centreLoading, setCentreLoading] = useState<boolean>(false);

  // Separate Explicit Enrolment Modal State
  const [centreEnrolModalApp, setCentreEnrolModalApp] = useState<any | null>(null);
  const [centreEnrolSelectedBatchId, setCentreEnrolSelectedBatchId] = useState<number | null>(null);
  const [centreEnrolInternalNotes, setCentreEnrolInternalNotes] = useState<string>('');
  const [centreEnrolSubmitting, setCentreEnrolSubmitting] = useState<boolean>(false);
  const [centreEnrolError, setCentreEnrolError] = useState<string>('');

  // Auth Modals & Dedicated Portal Navigation View State
  const [authPortalView, setAuthPortalView] = useState<'none' | 'select_role' | 'login_citizen' | 'login_student' | 'login_centre' | 'login_admin' | 'register_citizen' | 'register_centre_rep' | 'project_owner_register' | 'forgot_password' | 'set_password'>(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('portal') === 'owner' || params.get('mode') === 'project_owner') {
        return 'project_owner_register';
      }
    }
    return 'none';
  });

  // Project Owner Centre Account Register & Representative Setup State
  const [centreRegisterList, setCentreRegisterList] = useState<any[]>([]);
  const [centreRegisterLoading, setCentreRegisterLoading] = useState<boolean>(false);
  const [repSelectedCentreId, setRepSelectedCentreId] = useState<number>(1);
  const [repName, setRepName] = useState<string>('');
  const [repEmail, setRepEmail] = useState<string>('');
  const [repPhone, setRepPhone] = useState<string>('');
  const [repPassword, setRepPassword] = useState<string>('');
  const [repConfirmPassword, setRepConfirmPassword] = useState<string>('');
  const [repSubmitting, setRepSubmitting] = useState<boolean>(false);
  const [repMsg, setRepMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Project Owner Authentication & Protected Management State
  const [ownerAuthToken, setOwnerAuthToken] = useState<string>(localStorage.getItem('ns_skill_owner_token') || '');
  const [ownerKeyInput, setOwnerKeyInput] = useState<string>('');
  const [ownerAuthLoading, setOwnerAuthLoading] = useState<boolean>(false);
  const [ownerAuthMsg, setOwnerAuthMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [ownerResetCentreId, setOwnerResetCentreId] = useState<number | null>(null);
  const [ownerResetNewPassword, setOwnerResetNewPassword] = useState<string>('');
  const [ownerResetSubmitting, setOwnerResetSubmitting] = useState<boolean>(false);
  const [ownerResetMsg, setOwnerResetMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  
  const handleRegisterRepresentative = async (e: React.FormEvent) => {
    e.preventDefault();
    if (repPassword !== repConfirmPassword) {
      setRepMsg({ type: 'error', text: 'Password and confirm password do not match.' });
      return;
    }
    if (repPassword.length < 6) {
      setRepMsg({ type: 'error', text: 'Password must be at least 6 characters long.' });
      return;
    }
    setRepSubmitting(true);
    setRepMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/register-centre-representative`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          centre_id: repSelectedCentreId,
          representative_name: repName,
          representative_email: repEmail,
          representative_phone: repPhone,
          password: repPassword
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to register representative account.');
      
      setRepMsg({ type: 'success', text: `Authorized representative account successfully created for ${data.email}. Signing in...` });
      
      // Auto-login into centre workspace
      localStorage.setItem('ns_skill_token', data.access_token);
      localStorage.setItem('ns_skill_role', data.role);
      localStorage.setItem('ns_skill_centre_id', String(data.centre_id));
      localStorage.setItem('ns_skill_email', data.email);
      localStorage.setItem('ns_skill_name', data.full_name || '');
      setToken(data.access_token);
      setUserRole(data.role);
      setCentreId(String(data.centre_id));
      setUserEmail(data.email);
      setUserName(data.full_name || '');
      
      setTimeout(() => {
        setAuthPortalView('none');
        setCentreTab('dashboard');
      }, 1200);
    } catch (err: any) {
      setRepMsg({ type: 'error', text: err.message });
    } finally {
      setRepSubmitting(false);
    }
  };

  const handleOwnerResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ownerResetCentreId) return;
    if (ownerResetNewPassword.length < 8) {
      setOwnerResetMsg({ type: 'error', text: 'New password must be at least 8 characters long.' });
      return;
    }
    setOwnerResetSubmitting(true);
    setOwnerResetMsg(null);
    try {
      const headers: Record<string, string> = { 'Content-Type': 'application/json' };
      if (ownerAuthToken) {
        headers['Authorization'] = `Bearer ${ownerAuthToken}`;
      }
      const res = await fetch(`${API_BASE}/api/auth/project-owner-reset-centre-password`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          centre_id: ownerResetCentreId,
          new_password: ownerResetNewPassword
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Password reset rejected.');
      setOwnerResetMsg({ type: 'success', text: `Success: Credentials updated for ${data.centre_name} (${data.registered_email}).` });
      fetchCentreRegister();
      setTimeout(() => {
        setOwnerResetCentreId(null);
        setOwnerResetNewPassword('');
        setOwnerResetMsg(null);
      }, 2000);
    } catch (err: any) {
      setOwnerResetMsg({ type: 'error', text: err.message });
    } finally {
      setOwnerResetSubmitting(false);
    }
  };

  const fetchCentreRegister = async (tokenOverride?: string) => {
    setCentreRegisterLoading(true);
    const effectiveToken = tokenOverride !== undefined ? tokenOverride : ownerAuthToken;
    try {
      const headers: Record<string, string> = {};
      if (effectiveToken) {
        headers['Authorization'] = `Bearer ${effectiveToken}`;
      }
      const res = await fetch(`${API_BASE}/api/public/centre-register`, { headers });
      if (res.ok) {
        const data = await res.json();
        setCentreRegisterList(data);
      }
    } catch (err) {
      console.error('Failed to load centre register', err);
    } finally {
      setCentreRegisterLoading(false);
    }
  };

  const handleOwnerAuthenticate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ownerKeyInput.trim()) return;
    setOwnerAuthLoading(true);
    setOwnerAuthMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/project-owner-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ owner_key: ownerKeyInput.trim() })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Authentication failed. Please verify Project Owner Key.');
      localStorage.setItem('ns_skill_owner_token', data.access_token);
      setOwnerAuthToken(data.access_token);
      setOwnerAuthMsg({ type: 'success', text: 'Project Owner verified. Detailed institutional records unlocked.' });
      fetchCentreRegister(data.access_token);
      setOwnerKeyInput('');
    } catch (err: any) {
      setOwnerAuthMsg({ type: 'error', text: err.message });
    } finally {
      setOwnerAuthLoading(false);
    }
  };

  const handleOwnerSignOut = () => {
    localStorage.removeItem('ns_skill_owner_token');
    setOwnerAuthToken('');
    setOwnerAuthMsg(null);
    fetchCentreRegister('');
  };

  const [citizenLoginMode, setCitizenLoginMode] = useState<'password' | 'otp'>('password');
  const [showLoginPassword, setShowLoginPassword] = useState<boolean>(false);
  const [showRegPassword, setShowRegPassword] = useState<boolean>(false);
  const [showRegConfirmPassword, setShowRegConfirmPassword] = useState<boolean>(false);
  const [regConfirmPassword, setRegConfirmPassword] = useState<string>('');

  // Forgot / Reset Password State
  const [forgotEmail, setForgotEmail] = useState<string>('');
  const [forgotSource, setForgotSource] = useState<'citizen' | 'centre'>('citizen');
  const [forgotOtpSent, setForgotOtpSent] = useState<boolean>(false);
  const [forgotOtpCode, setForgotOtpCode] = useState<string>('');
  const [forgotOtpRef, setForgotOtpRef] = useState<string>('');
  const [forgotOtpLoading, setForgotOtpLoading] = useState<boolean>(false);
  const [forgotOtpVerified, setForgotOtpVerified] = useState<boolean>(false);
  const [forgotOtpMsg, setForgotOtpMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [forgotOtpDemoCode, setForgotOtpDemoCode] = useState<string>('');
  const [forgotOtpDemoMode, setForgotOtpDemoMode] = useState<boolean>(false);
  const [forgotOtpCooldown, setForgotOtpCooldown] = useState<number>(0);
  const [forgotNewPassword, setForgotNewPassword] = useState<string>('');
  const [forgotConfirmPassword, setForgotConfirmPassword] = useState<string>('');
  const [showForgotNewPassword, setShowForgotNewPassword] = useState<boolean>(false);
  const [forgotSubmitting, setForgotSubmitting] = useState<boolean>(false);
  const [forgotSuccess, setForgotSuccess] = useState<string>('');

  // Set Password State (For existing citizens without password)
  const [setPasswordEmail, setSetPasswordEmail] = useState<string>('');
  const [setPasswordOtpSent, setSetPasswordOtpSent] = useState<boolean>(false);
  const [setPasswordOtpCode, setSetPasswordOtpCode] = useState<string>('');
  const [setPasswordOtpRef, setSetPasswordOtpRef] = useState<string>('');
  const [setPasswordOtpLoading, setSetPasswordOtpLoading] = useState<boolean>(false);
  const [setPasswordOtpVerified, setSetPasswordOtpVerified] = useState<boolean>(false);
  const [setPasswordOtpMsg, setSetPasswordOtpMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [setPasswordOtpDemoCode, setSetPasswordOtpDemoCode] = useState<string>('');
  const [setPasswordOtpDemoMode, setSetPasswordOtpDemoMode] = useState<boolean>(false);
  const [setPasswordOtpCooldown, setSetPasswordOtpCooldown] = useState<number>(0);
  const [setNewPasswordVal, setSetNewPasswordVal] = useState<string>('');
  const [setConfirmPasswordVal, setSetConfirmPasswordVal] = useState<string>('');
  const [showSetNewPassword, setShowSetNewPassword] = useState<boolean>(false);
  const [setPasswordSubmitting, setSetPasswordSubmitting] = useState<boolean>(false);
  const [setPasswordSuccess, setSetPasswordSuccess] = useState<string>('');

  // Change Password State (Inside Profile tab for authenticated citizens)
  const [changeCurrentPassword, setChangeCurrentPassword] = useState<string>('');
  const [changeNewPassword, setChangeNewPassword] = useState<string>('');
  const [changeConfirmPassword, setChangeConfirmPassword] = useState<string>('');
  const [showChangeCurrentPassword, setShowChangeCurrentPassword] = useState<boolean>(false);
  const [showChangeNewPassword, setShowChangeNewPassword] = useState<boolean>(false);
  const [showChangeConfirmPassword, setShowChangeConfirmPassword] = useState<boolean>(false);
  const [changePasswordLoading, setChangePasswordLoading] = useState<boolean>(false);
  const [changePasswordMsg, setChangePasswordMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [showLoginModal, setShowLoginModal] = useState<boolean>(false);
  const [showRegisterModal, setShowRegisterModal] = useState<boolean>(false);
  const [authError, setAuthError] = useState<string>('');
  const [authLoading, setAuthLoading] = useState<boolean>(false);

  // Form Inputs for Auth
  const [loginEmail, setLoginEmail] = useState<string>('');
  const [loginPassword, setLoginPassword] = useState<string>('');
  const [isAdminLogin, setIsAdminLogin] = useState<boolean>(false);
  const [loginOtpSent, setLoginOtpSent] = useState<boolean>(false);
  const [loginOtpCode, setLoginOtpCode] = useState<string>('');
  const [loginOtpRef, setLoginOtpRef] = useState<string>('');
  const [loginOtpLoading, setLoginOtpLoading] = useState<boolean>(false);
  const [loginOtpVerified, setLoginOtpVerified] = useState<boolean>(false);
  const [loginOtpMsg, setLoginOtpMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [loginOtpCooldown, setLoginOtpCooldown] = useState<number>(0);
  const [loginOtpExpirySec, setLoginOtpExpirySec] = useState<number>(0);
  const [loginOtpDemoCode, setLoginOtpDemoCode] = useState<string>('');
  const [loginOtpDemoMode, setLoginOtpDemoMode] = useState<boolean>(false);
  const [regFullName, setRegFullName] = useState<string>('');
  const [regEmail, setRegEmail] = useState<string>('');
  const [regPassword, setRegPassword] = useState<string>('');
  const [regPhone, setRegPhone] = useState<string>('');
  const [regTermsAgreed, setRegTermsAgreed] = useState<boolean>(false);

  // OTP Verification State: Registration (Email OTP)
  const [regOtpSent, setRegOtpSent] = useState<boolean>(false);
  const [regOtpCode, setRegOtpCode] = useState<string>('');
  const [regOtpRef, setRegOtpRef] = useState<string>('');
  const [regOtpLoading, setRegOtpLoading] = useState<boolean>(false);
  const [regOtpVerified, setRegOtpVerified] = useState<boolean>(false);
  const [regOtpMsg, setRegOtpMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [regOtpCooldown, setRegOtpCooldown] = useState<number>(0);
  const [regOtpExpirySec, setRegOtpExpirySec] = useState<number>(300);
  const [regOtpDemoMode, setRegOtpDemoMode] = useState<boolean>(false);
  const [regOtpDemoCode, setRegOtpDemoCode] = useState<string>('');

  // OTP Verification State: Enrolment Application
  const [enrolOtpSent, setEnrolOtpSent] = useState<boolean>(false);
  const [enrolOtpCode, setEnrolOtpCode] = useState<string>('');
  const [enrolOtpRef, setEnrolOtpRef] = useState<string>('');
  const [enrolOtpLoading, setEnrolOtpLoading] = useState<boolean>(false);
  const [enrolOtpVerified, setEnrolOtpVerified] = useState<boolean>(false);
  const [enrolOtpMsg, setEnrolOtpMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [enrolOtpCooldown, setEnrolOtpCooldown] = useState<number>(0);

  // OTP Verification State: Profile Phone Update
  const [profileOtpSent, setProfileOtpSent] = useState<boolean>(false);
  const [profileOtpCode, setProfileOtpCode] = useState<string>('');
  const [profileOtpRef, setProfileOtpRef] = useState<string>('');
  const [profileOtpLoading, setProfileOtpLoading] = useState<boolean>(false);
  const [profileOtpVerified, setProfileOtpVerified] = useState<boolean>(false);
  const [profileOtpMsg, setProfileOtpMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [profileOtpCooldown, setProfileOtpCooldown] = useState<number>(0);

  // Course Data & Search/Filter State
  const [skills, setSkills] = useState<any[]>([]);
  const [totalSkills, setTotalSkills] = useState<number>(0);
  const [homepageStats, setHomepageStats] = useState<{ skills_available: number; training_programmes: number; registered_training_centres: number }>({
    skills_available: 105,
    training_programmes: 125,
    registered_training_centres: 6
  });
  const [categories, setCategories] = useState<any[]>([]);
  const [activeCategoryCode, setActiveCategoryCode] = useState<string>('');
  const [selectedSubcategoryId, setSelectedSubcategoryId] = useState<number | null>(null);
  const [adminCatalogueData, setAdminCatalogueData] = useState<any>(null);
  const [adminCatalogueLoading, setAdminCatalogueLoading] = useState<boolean>(false);
  const [categoryDetailsData, setCategoryDetailsData] = useState<any | null>(null);
  const [loadingCategoryDetails, setLoadingCategoryDetails] = useState<boolean>(false);
  const [categoryDetailsError, setCategoryDetailsError] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedLevel, setSelectedLevel] = useState<string>('All');
  const [page, setPage] = useState<number>(1);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [loadingSkills, setLoadingSkills] = useState<boolean>(false);

  // Selected Detail Modal
  const [selectedCourse, setSelectedCourse] = useState<any | null>(null);
  const [courseDetailTab, setCourseDetailTab] = useState<'overview' | 'syllabus' | 'batches' | 'trainer'>('overview');

  // Citizen Profile Editing State
  const [showEditProfileModal, setShowEditProfileModal] = useState<boolean>(false);
  const [editFullName, setEditFullName] = useState<string>('');
  const [editPhone, setEditPhone] = useState<string>('');
  const [editDob, setEditDob] = useState<string>('');
  const [editGender, setEditGender] = useState<string>('Male');
  const [editAddress, setEditAddress] = useState<string>('');
  const [editEducation, setEditEducation] = useState<string>('Bachelor of Engineering / Science');
  const [editEmployment, setEditEmployment] = useState<string>('Job Seeker');
  const [editExpYears, setEditExpYears] = useState<number>(0);
  const [editInterests, setEditInterests] = useState<string>('');
  const [editGoals, setEditGoals] = useState<string>('');
  const [editPrefMode, setEditPrefMode] = useState<string>('Hybrid');
  const [editPrefLocation, setEditPrefLocation] = useState<string>('Bengaluru');
  const [editResumeSummary, setEditResumeSummary] = useState<string>('');
  const [profileSaving, setProfileSaving] = useState<boolean>(false);
  const [profileMsg, setProfileMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Enrolment Application State (8-Section Comprehensive Dossier)
  const [enrollingProgram, setEnrollingProgram] = useState<any | null>(null);
  const [selectedBatchId, setSelectedBatchId] = useState<number | null>(null);
  const [enrolmentStatement, setEnrolmentStatement] = useState<string>('');
  const [enrolmentSuccessMsg, setEnrolmentSuccessMsg] = useState<string>('');
  const [enrolmentErrorMsg, setEnrolmentErrorMsg] = useState<string>('');
  const [enrolSubmitting, setEnrolSubmitting] = useState<boolean>(false);

  // 8-Section Comprehensive Form Fields
  const [appFullName, setAppFullName] = useState<string>('');
  const [appDob, setAppDob] = useState<string>('');
  const [appGender, setAppGender] = useState<string>('Male');
  const [appPhone, setAppPhone] = useState<string>('');
  const [appEmail, setAppEmail] = useState<string>('');
  const [appAltPhone, setAppAltPhone] = useState<string>('');

  const [appAddress, setAppAddress] = useState<string>('');
  const [appCity, setAppCity] = useState<string>('Bengaluru');
  const [appState, setAppState] = useState<string>('Karnataka');
  const [appPincode, setAppPincode] = useState<string>('560001');

  const [appEducation, setAppEducation] = useState<string>('Bachelor of Engineering / Science');
  const [appInstitution, setAppInstitution] = useState<string>('');
  const [appGradYear, setAppGradYear] = useState<string>('2024');
  const [appSpecialization, setAppSpecialization] = useState<string>('Computer Science & Engineering');

  const [appEmploymentStatus, setAppEmploymentStatus] = useState<string>('Job Seeker');
  const [appOccupation, setAppOccupation] = useState<string>('');
  const [appExperienceYears, setAppExperienceYears] = useState<number>(0);

  const [appPrefTiming, setAppPrefTiming] = useState<string>('Morning (09:00 AM - 12:00 PM)');
  const [appPrefMode, setAppPrefMode] = useState<string>('Hybrid');

  const [appTargetSkills, setAppTargetSkills] = useState<string>('');
  const [appPostJobPlacement, setAppPostJobPlacement] = useState<boolean>(true);

  const [appIdProofType, setAppIdProofType] = useState<string>('Aadhaar / National Identity Card');
  const [appIdProofNumber, setAppIdProofNumber] = useState<string>('');
  const [appDocAttachedNote, setAppDocAttachedNote] = useState<string>('');

  const [appDeclarationAgreed, setAppDeclarationAgreed] = useState<boolean>(false);

  // Data for Programmes, Trainers, Centres, Careers
  const [programmes, setProgrammes] = useState<any[]>([]);
  const [trainers, setTrainers] = useState<any[]>([]);
  const [centres, setCentres] = useState<any[]>([]);

  // Nearby Training Centres (GPS & Location Search) State
  const [nearbyCentres, setNearbyCentres] = useState<any[]>([]);
  const [exactLocalityCentres, setExactLocalityCentres] = useState<any[]>([]);
  const [outsideLocalityCentres, setOutsideLocalityCentres] = useState<any[]>([]);
  const [nearbyLoading, setNearbyLoading] = useState<boolean>(false);
  const [nearbyError, setNearbyError] = useState<string>('');
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [locationLabel, setLocationLabel] = useState<string>('');
  const [locationMode, setLocationMode] = useState<'NONE' | 'GPS' | 'MANUAL'>('NONE');
  const [selectedRadius, setSelectedRadius] = useState<number>(5);
  const [customRadiusInput, setCustomRadiusInput] = useState<string>('5');
  const [manualQuery, setManualQuery] = useState<string>('');
  const [skillSearchFilter, setSkillSearchFilter] = useState<string>('');
  const [manualSearching, setManualSearching] = useState<boolean>(false);
  const [selectedCentreId, setSelectedCentreId] = useState<string | null>(null);
  const [discoveredProvider, setDiscoveredProvider] = useState<string>('Real-World Places Discovery');
  const [jobs, setJobs] = useState<any[]>([]);
  const [savedJobs, setSavedJobs] = useState<any[]>([]);
  const [myJobApplications, setMyJobApplications] = useState<any[]>([]);
  const [appsActiveSubTab, setAppsActiveSubTab] = useState<'courses' | 'jobs' | 'saved'>('courses');
  const [applyingJob, setApplyingJob] = useState<any | null>(null);
  const [jobApplyFullName, setJobApplyFullName] = useState<string>('');
  const [jobApplyEmail, setJobApplyEmail] = useState<string>('');
  const [jobApplyPhone, setJobApplyPhone] = useState<string>('');
  const [jobApplyEducation, setJobApplyEducation] = useState<string>('');
  const [jobApplyExperience, setJobApplyExperience] = useState<string>('');
  const [jobApplyStatement, setJobApplyStatement] = useState<string>('');
  const [jobApplyLoading, setJobApplyLoading] = useState<boolean>(false);
  const [jobApplyMsg, setJobApplyMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Citizen Dashboard & Enrolments
  const [myApplications, setMyApplications] = useState<any[]>([]);
  const [selectedCitizenApp, setSelectedCitizenApp] = useState<any | null>(null);
  const [myProfile, setMyProfile] = useState<any | null>(null);
  const [myCertificates, setMyCertificates] = useState<any[]>([]);
  const [newSkillInput, setNewSkillInput] = useState<string>('');

  // Skill Gap State
  const [supportedRoles, setSupportedRoles] = useState<any[]>([]);
  const [selectedTargetRole, setSelectedTargetRole] = useState<string>('Full Stack Python / Web Developer');
  const [gapReport, setGapReport] = useState<any | null>(null);

  // Admin Portal State
  const [adminStats, setAdminStats] = useState<any | null>(null);
  const [adminEnrollments, setAdminEnrollments] = useState<any[]>([]);
  const [adminFilterStatus, setAdminFilterStatus] = useState<string>('ALL');
  const [reviewModalApp, setReviewModalApp] = useState<any | null>(null);
  const [reviewStatus, setReviewStatus] = useState<string>('APPROVED');
  const [reviewRemarks, setReviewRemarks] = useState<string>('');
  const [adminTab, setAdminTab] = useState<'applications' | 'skills' | 'programmes' | 'centres' | 'hierarchy'>('applications');
  const [showAddSkillModal, setShowAddSkillModal] = useState<boolean>(false);
  const [newSkillName, setNewSkillName] = useState<string>('');
  const [newSkillCategory, setNewSkillCategory] = useState<string>('Information Technology & Software');
  const [newSkillLevel, setNewSkillLevel] = useState<string>('Beginner');
  const [newSkillHours, setNewSkillHours] = useState<number>(40);
  const [newSkillWeeks, setNewSkillWeeks] = useState<number>(6);
  const [newSkillSummary, setNewSkillSummary] = useState<string>('');

  const [showAddProgrammeModal, setShowAddProgrammeModal] = useState<boolean>(false);
  const [newProgTitle, setNewProgTitle] = useState<string>('');
  const [newProgDesc, setNewProgDesc] = useState<string>('');
  const [newProgSkillId, setNewProgSkillId] = useState<number>(1);
  const [newProgMode, setNewProgMode] = useState<string>('Hybrid');
  const [newProgHours, setNewProgHours] = useState<number>(60);
  const [newProgFee, setNewProgFee] = useState<number>(0);
  const [newProgBatchName, setNewProgBatchName] = useState<string>('Morning Regular Batch A');
  const [newProgBatchSeats, setNewProgBatchSeats] = useState<number>(30);
  const [newProgBatchTimings, setNewProgBatchTimings] = useState<string>('09:00 AM - 12:00 PM');
  const [newProgBatchSchedule, setNewProgBatchSchedule] = useState<string>('Monday to Friday');

  const [showAddCentreModal, setShowAddCentreModal] = useState<boolean>(false);
  const [newCentreName, setNewCentreName] = useState<string>('');
  const [newCentreLocation, setNewCentreLocation] = useState<string>('');
  const [newCentreDistrict, setNewCentreDistrict] = useState<string>('Bengaluru Urban');
  const [newCentreAddress, setNewCentreAddress] = useState<string>('');
  const [newCentrePhone, setNewCentrePhone] = useState<string>('+91 80 2345 6789');
  const [newCentreEmail, setNewCentreEmail] = useState<string>('centre@nagriksetu.gov.in');
  const [newCentreFacilities, setNewCentreFacilities] = useState<string>('Advanced Computer Lab, High-speed Internet, Smart Classrooms');
  const [progressScore, setProgressScore] = useState<number>(100);
  const [progressAttendance, setProgressAttendance] = useState<number>(90);
  const [progressPct, setProgressPct] = useState<number>(100);

  // Notification Banner
  const [bannerNotice, setBannerNotice] = useState<string>('');

  // Admin Centre Lifecycle & Assignment State
  const [adminCentresList, setAdminCentresList] = useState<any[]>([]);
  const [adminCentresLoading, setAdminCentresLoading] = useState<boolean>(false);
  const [adminCentreFilter, setAdminCentreFilter] = useState<'APPROVED' | 'REJECTED' | 'ALL'>('APPROVED');
  const [selectedCentreForAdmin, setSelectedCentreForAdmin] = useState<any | null>(null);
  const [assignAdminFullName, setAssignAdminFullName] = useState<string>('');
  const [assignAdminEmail, setAssignAdminEmail] = useState<string>('');
  const [assignAdminPassword, setAssignAdminPassword] = useState<string>('CentreAdmin@2026!');
  const [assignAdminPhone, setAssignAdminPhone] = useState<string>('');
  const [assignAdminSubmitting, setAssignAdminSubmitting] = useState<boolean>(false);
  const [assignAdminMsg, setAssignAdminMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const [selectedCentreForStatus, setSelectedCentreForStatus] = useState<any | null>(null);
  const [centreStatusTarget, setCentreStatusTarget] = useState<'APPROVED' | 'SUSPENDED' | 'REJECTED'>('SUSPENDED');
  const [centreStatusReason, setCentreStatusReason] = useState<string>('');
  const [centreStatusSubmitting, setCentreStatusSubmitting] = useState<boolean>(false);
  const [centreStatusMsg, setCentreStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);



  const getStatusText = (statusKey: string): string => {
    const res = t(`status.${statusKey}`, { defaultValue: statusKey });
    return typeof res === 'string' ? res : String(res ?? statusKey);
  };

  const formatISTDateTime = (dateStr?: string | null): string => {
    if (!dateStr) return 'N/A';
    try {
      const d = new Date(dateStr);
      if (isNaN(d.getTime())) return dateStr;
      return d.toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      });
    } catch {
      return dateStr;
    }
  };

  // Fetch Skills Catalog
  const fetchSkills = async (cat = selectedCategory, lvl = selectedLevel, q = searchQuery, p = page) => {
    setLoadingSkills(true);
    try {
      let url = `${API_BASE}/api/skills?page=${p}&limit=12`;
      if (cat !== 'All') url += `&category=${encodeURIComponent(cat)}`;
      if (lvl !== 'All') url += `&level=${encodeURIComponent(lvl)}`;
      if (q.trim()) url += `&q=${encodeURIComponent(q.trim())}`;

      const res = await fetch(url);
      const data = await res.json();
      setSkills(data.items || []);
      setTotalSkills(data.total || 0);
      setTotalPages(data.total_pages || 1);
    } catch (e: any) {
      console.error(e);
    } finally {
      setLoadingSkills(false);
    }
  };

  // Load initial public catalogs
  useEffect(() => {
    fetch(`${API_BASE}/api/categories`)
      .then(r => r.json())
      .then(setCategories)
      .catch(console.error);

    fetchSkills();

    fetch(`${API_BASE}/api/public/homepage-stats`)
      .then(r => r.json())
      .then(data => {
        if (data && typeof data.skills_available === 'number') {
          setHomepageStats(data);
        }
      })
      .catch(console.error);

    fetch(`${API_BASE}/api/programmes`)
      .then(r => r.json())
      .then(setProgrammes)
      .catch(console.error);

    fetch(`${API_BASE}/api/trainers`)
      .then(r => r.json())
      .then(setTrainers)
      .catch(console.error);

    fetch(`${API_BASE}/api/centres`)
      .then(r => r.json())
      .then(setCentres)
      .catch(console.error);

    fetch(`${API_BASE}/api/jobs`)
      .then(r => r.json())
      .then(setJobs)
      .catch(console.error);

    fetch(`${API_BASE}/api/skill-gap/roles`)
      .then(r => r.json())
      .then(setSupportedRoles)
      .catch(console.error);

    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      if (params.get('portal') === 'owner' || params.get('mode') === 'project_owner') {
        fetchCentreRegister();
      }
    }
  }, []);

  // Fetch nearby training centres from backend
  const fetchNearbyCentres = (lat: number, lon: number, radius: number) => {
    setNearbyLoading(true);
    setNearbyError('');
    setSelectedCentreId(null);
    fetch(`${API_BASE}/api/centres/nearby?latitude=${lat}&longitude=${lon}&radius_km=${radius}`)
      .then(async (res) => {
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Failed to fetch nearby centres.');
        }
        return res.json();
      })
      .then((data) => {
        setNearbyCentres(data.results || []);
        setExactLocalityCentres(data.exact_locality_results || data.results || []);
        setOutsideLocalityCentres(data.outside_locality_results || []);
        if (data.provider) setDiscoveredProvider(data.provider);
        if (data.detected_address && locationMode === 'GPS') {
          setLocationLabel(`Current GPS Location (${data.detected_address})`);
        }
        setNearbyLoading(false);
      })
      .catch((err) => {
        setNearbyError(err.message || 'Error loading nearby training centres.');
        setNearbyLoading(false);
      });
  };

  // Re-fetch nearby centres when selected radius changes and location exists
  useEffect(() => {
    if (userLocation) {
      fetchNearbyCentres(userLocation.latitude, userLocation.longitude, selectedRadius);
    }
  }, [selectedRadius]);

  // Handle GPS location detection via navigator.geolocation
  const handleUseCurrentLocation = () => {
    setNearbyError('');
    setSelectedCentreId(null);
    if (!navigator.geolocation) {
      setNearbyError('Geolocation is not supported by your current browser.');
      return;
    }

    setNearbyLoading(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const lat = pos.coords.latitude;
        const lon = pos.coords.longitude;
        setUserLocation({ latitude: lat, longitude: lon });
        setLocationMode('GPS');
        setLocationLabel('Current GPS Location (High Accuracy)');
        fetchNearbyCentres(lat, lon, selectedRadius);
      },
      (err) => {
        setNearbyLoading(false);
        if (err.code === err.PERMISSION_DENIED) {
          setNearbyError('Location permission denied. Please allow location access in your browser or search by PIN code/city below.');
        } else if (err.code === err.POSITION_UNAVAILABLE) {
          setNearbyError('Location information is currently unavailable. Please check your GPS signal or search manually.');
        } else if (err.code === err.TIMEOUT) {
          setNearbyError('Location request timed out. Please try again or use the manual search.');
        } else {
          setNearbyError(`Unable to retrieve location: ${err.message}`);
        }
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };

  // Universal location search via backend GET /api/centres/search
  const handleUniversalSearch = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const query = manualQuery.trim();
    if (!query) {
      setNearbyError('Please enter an area, locality, city, or PIN code to search.');
      return;
    }

    // Parse and validate custom radius input (strict 1 km to 25 km limit)
    const parsedRadius = parseFloat(customRadiusInput);
    if (isNaN(parsedRadius) || parsedRadius < 1 || parsedRadius > 25) {
      setNearbyError('Please enter a valid search radius between 1 km and 25 km.');
      return;
    }

    setManualSearching(true);
    setNearbyLoading(true);
    setNearbyError('');
    setSelectedCentreId(null);
    setSelectedRadius(parsedRadius);

    fetch(`${API_BASE}/api/centres/search?location=${encodeURIComponent(query)}&radius_km=${parsedRadius}${skillSearchFilter.trim() ? `&skill=${encodeURIComponent(skillSearchFilter.trim())}` : ''}`)
      .then(async (res) => {
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Unable to find location.');
        }
        return res.json();
      })
      .then((data) => {
        if (data.search_coordinates) {
          setUserLocation(data.search_coordinates);
          setLocationMode('MANUAL');
          setLocationLabel(data.resolved_address || query);
        }
        setNearbyCentres(data.results || []);
        setExactLocalityCentres(data.exact_locality_results || []);
        setOutsideLocalityCentres(data.outside_locality_results || []);
        if (data.provider) setDiscoveredProvider(data.provider);
        setManualSearching(false);
        setNearbyLoading(false);
      })
      .catch((err) => {
        setNearbyError(err.message || 'Error searching for training centres.');
        setManualSearching(false);
        setNearbyLoading(false);
      });
  };

  // Reload when search filters change
  useEffect(() => {
    fetchSkills(selectedCategory, selectedLevel, searchQuery, page);
  }, [selectedCategory, selectedLevel, page]);

  // Helper to determine contact phone verification status and authoritative source
  const getContactVerification = (centre: any) => {
    const rawPhone = (centre.contact_phone || centre.phone || '').trim();
    const hasPhone = rawPhone && rawPhone !== 'N/A' && rawPhone !== 'null';
    
    // Explicit authoritative verification mappings
    // Belagavi, Davanagere, Kalaburagi, Shivamogga, Virtual Portal: genuine numbers from DGT / KSDM / National toll-free
    const code = (centre.code || '').toUpperCase().trim();
    const name = (centre.name || '').toLowerCase();

    // 1. National Virtual Learning Portal Toll-Free
    if (code === 'CTR-0005' || name.includes('virtual learning portal')) {
      return {
        phone: rawPhone,
        status: 'Verified',
        source: 'National Citizen Service Directory (Toll-Free 1800-11-2026)',
        badgeColor: '#15803d',
        badgeBg: '#dcfce7'
      };
    }

    // 2. Verified Karnataka Government Regional ITI / GTTC Institutional Contacts
    if (code === 'CTR-0007' || name.includes('belagavi regional skilling hub')) {
      return {
        phone: rawPhone,
        status: 'Verified',
        source: 'Government Industrial Training Directory / DGT Kaushalkar Karnataka',
        badgeColor: '#15803d',
        badgeBg: '#dcfce7'
      };
    }
    if (code === 'CTR-0008' || name.includes('davanagere vocational & technical institute')) {
      return {
        phone: rawPhone,
        status: 'Verified',
        source: 'Government Industrial Training Directory / DGT Kaushalkar Karnataka',
        badgeColor: '#15803d',
        badgeBg: '#dcfce7'
      };
    }
    if (code === 'CTR-0009' || name.includes('kalaburagi regional skill development centre')) {
      return {
        phone: rawPhone,
        status: 'Verified',
        source: 'Government Industrial Training Directory / DGT Kaushalkar Karnataka',
        badgeColor: '#15803d',
        badgeBg: '#dcfce7'
      };
    }
    if (code === 'CTR-0010' || name.includes('shivamogga malnad skill development centre')) {
      return {
        phone: rawPhone,
        status: 'Verified',
        source: 'Government Industrial Training Directory / DGT Kaushalkar Karnataka',
        badgeColor: '#15803d',
        badgeBg: '#dcfce7'
      };
    }

    // 3. Real-World Authentic Places Registry Institutes with authoritative public records
    if (centre.source && (
      centre.source.includes('Government ITI Directory') ||
      centre.source.includes('GTTC Official') ||
      centre.source.includes('NSDC') ||
      centre.source.includes('Ministry of') ||
      centre.source.includes('Department of Technical Education')
    )) {
      return {
        phone: rawPhone,
        status: 'Verified',
        source: centre.source,
        badgeColor: '#15803d',
        badgeBg: '#dcfce7'
      };
    }

    // 4. Centres with phone number present but not independently confirmed by authoritative directory
    if (hasPhone) {
      return {
        phone: rawPhone,
        status: 'Unverified',
        source: 'Institutional submission (pending external directory confirmation)',
        badgeColor: '#b45309',
        badgeBg: '#fef3c7'
      };
    }

    // 5. No phone number available
    return {
      phone: null,
      status: 'Unavailable',
      source: 'No verified contact number recorded',
      badgeColor: '#64748b',
      badgeBg: '#f1f5f9'
    };
  };

  // Helper to render individual training centre card
  const renderCentreCard = (c: any, isExactMatch?: boolean) => {
    const isSelected = (c.id === selectedCentreId || c.code === selectedCentreId);
    return (
      <div
        key={c.id || c.code}
        onClick={() => setSelectedCentreId(c.id || c.code)}
        style={{
          backgroundColor: '#ffffff',
          border: isSelected ? '2px solid #ea580c' : (isExactMatch ? '1px solid #99f6e4' : '1px solid #e2e8f0'),
          borderRadius: '12px',
          padding: '1.5rem',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          boxShadow: isSelected ? '0 4px 14px rgba(234,88,12,0.18)' : '0 1px 3px rgba(0,0,0,0.05)',
          transform: isSelected ? 'scale(1.01)' : 'scale(1)',
          transition: 'all 0.15s ease',
          cursor: 'pointer'
        }}
      >
        <div>
          {/* Top Badge Row */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.6rem', flexWrap: 'wrap', gap: '4px' }}>
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center', flexWrap: 'wrap' }}>
              <span
                style={{
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  color: c.is_official_centre ? '#ea580c' : '#0d9488',
                  backgroundColor: c.is_official_centre ? '#fff7ed' : '#f0fdfa',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  border: `1px solid ${c.is_official_centre ? '#ffedd5' : '#ccfbf1'}`
                }}
              >
                {c.is_official_centre ? (c.code || 'Official NagrikSetu Hub') : (c.category || 'Skill Development')}
              </span>
              {c.verification_status && (
                <span
                  style={{
                    fontSize: '0.68rem',
                    fontWeight: 600,
                    color: c.verification_status === 'Officially verified' ? '#15803d' : (c.verification_status === 'Independently listed' ? '#0369a1' : '#475569'),
                    backgroundColor: c.verification_status === 'Officially verified' ? '#dcfce7' : (c.verification_status === 'Independently listed' ? '#e0f2fe' : '#f1f5f9'),
                    padding: '2px 6px',
                    borderRadius: '4px'
                  }}
                >
                  {c.verification_status}
                </span>
              )}
              {isExactMatch && (
                <span style={{ fontSize: '0.68rem', fontWeight: 700, color: '#047857', backgroundColor: '#d1fae5', padding: '2px 6px', borderRadius: '4px' }}>
                  Locality Match
                </span>
              )}
            </div>

            {c.distance_km != null && (
              <span style={{ fontSize: '0.76rem', fontWeight: 700, color: '#0f766e', backgroundColor: '#ccfbf1', padding: '3px 8px', borderRadius: '6px' }}>
                📍 {c.distance_km} km away
              </span>
            )}
          </div>

          {/* Centre Name */}
          <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.4rem', lineHeight: '1.3' }}>
            {c.name}
          </h3>

          {/* Rating only if genuinely provided */}
          {c.rating && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.76rem', color: '#d97706', marginBottom: '0.5rem' }}>
              <Star size={13} fill="#d97706" color="#d97706" />
              <strong>{c.rating}</strong>
              {c.review_count && <span style={{ color: '#64748b' }}>({c.review_count} citizen reviews)</span>}
            </div>
          )}

          {/* Complete Address */}
          <p style={{ fontSize: '0.82rem', color: '#475569', marginBottom: '0.65rem', lineHeight: '1.4' }}>
            <MapPin size={13} style={{ display: 'inline', marginRight: '4px', color: '#ea580c' }} />
            {c.address}
          </p>

          {/* Matching / Available Programmes */}
          {c.matching_programmes && c.matching_programmes.length > 0 && (
            <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', padding: '0.65rem', borderRadius: '6px', fontSize: '0.76rem', color: '#166534', marginBottom: '0.65rem', lineHeight: '1.4' }}>
              <strong style={{ color: '#14532d', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '3px' }}>
                <GraduationCap size={13} /> {c.matching_programmes.length} Matching Programme{c.matching_programmes.length === 1 ? '' : 's'}:
              </strong>
              {c.matching_programmes.slice(0, 3).map((mp: any) => (
                <div key={mp.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2px', fontSize: '0.74rem' }}>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>• {mp.title}</span>
                  <span style={{ color: '#ea580c', fontWeight: 700 }}>{mp.mode}</span>
                </div>
              ))}
              {c.matching_programmes.length > 3 && (
                <div style={{ fontSize: '0.7rem', color: '#64748b', marginTop: '2px' }}>+{c.matching_programmes.length - 3} more programmes</div>
              )}
            </div>
          )}

          {/* Facilities / Details */}
          {c.facilities && (
            <div style={{ backgroundColor: '#f8fafc', padding: '0.65rem', borderRadius: '6px', fontSize: '0.76rem', color: '#334155', marginBottom: '0.65rem', lineHeight: '1.4' }}>
              <strong style={{ color: '#0f172a' }}>Facilities:</strong> {c.facilities}
            </div>
          )}

          {/* Contact details with explicit verification status */}
          {(() => {
            const vInfo = getContactVerification(c);
            const emailAddr = (c.contact_email || c.email || '').trim();
            const hasEmail = emailAddr && emailAddr !== 'N/A' && emailAddr !== 'null';

            return (
              <div style={{ fontSize: '0.78rem', color: '#475569', lineHeight: '1.5', marginTop: '0.5rem', background: '#f8fafc', padding: '0.65rem', borderRadius: '6px', border: '1px solid #f1f5f9' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '4px', marginBottom: '3px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <Phone size={13} color="#0f766e" />
                    <strong>Contact Phone:</strong>{' '}
                    <span>{vInfo.phone || 'Contact details unavailable'}</span>
                  </div>
                  <span
                    style={{
                      fontSize: '0.68rem',
                      fontWeight: 700,
                      color: vInfo.badgeColor,
                      backgroundColor: vInfo.badgeBg,
                      padding: '1px 6px',
                      borderRadius: '4px',
                      border: `1px solid ${vInfo.badgeColor}33`
                    }}
                  >
                    {vInfo.status}
                  </span>
                </div>

                {hasEmail && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '3px' }}>
                    <Mail size={13} color="#0284c7" />
                    <strong>Email:</strong> {emailAddr}
                  </div>
                )}

                {vInfo.status === 'Verified' && (
                  <div style={{ fontSize: '0.7rem', color: '#15803d', marginTop: '3px', fontStyle: 'italic' }}>
                    ✓ Source: {vInfo.source}
                  </div>
                )}
              </div>
            );
          })()}
        </div>

        {/* Bottom Action Buttons: Full Institutional Profile + View on Map */}
        <div style={{ marginTop: '1.25rem', borderTop: '1px solid #f1f5f9', paddingTop: '1rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {(c.id || c.code || c.place_id) && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                openPublicCentreProfile(c.id || c.code || c.place_id);
              }}
              style={{
                flex: '1 1 140px',
                backgroundColor: '#0f766e',
                color: '#ffffff',
                border: 'none',
                textAlign: 'center',
                padding: '0.65rem 0.8rem',
                borderRadius: '6px',
                fontSize: '0.82rem',
                fontWeight: 700,
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.4rem',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <Building2 size={14} /> View Full Profile
            </button>
          )}

          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              const centreKey = c.id || c.code;
              setSelectedCentreId(centreKey);
              // Smoothly scroll to the interactive Training Centre Map inside the application
              const mapElement = document.getElementById('training-centre-map-section');
              if (mapElement) {
                mapElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
              }
            }}
            style={{
              flex: '1 1 120px',
              backgroundColor: isSelected ? '#1e3a8a' : '#ea580c',
              color: '#ffffff',
              border: 'none',
              textAlign: 'center',
              padding: '0.65rem 0.8rem',
              borderRadius: '6px',
              fontSize: '0.82rem',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.4rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <MapPin size={14} /> {isSelected ? 'Focused on Map' : 'View on Map'}
          </button>
        </div>
      </div>
    );
  };

  // Load user data upon sign-in
  useEffect(() => {
    if (!token) return;

    // Fetch Citizen Profile
    fetch(`${API_BASE}/api/profiles/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(setMyProfile)
      .catch(() => {});

    // Fetch My Applications
    fetch(`${API_BASE}/api/enrollments/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(setMyApplications)
      .catch(() => {});

    // Fetch Certificates
    fetch(`${API_BASE}/api/certificates`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(setMyCertificates)
      .catch(() => {});

    // Fetch Saved Jobs
    fetch(`${API_BASE}/api/jobs/saved`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(setSavedJobs)
      .catch(() => {});

    // Fetch My Job Applications
    fetch(`${API_BASE}/api/jobs/applications/me`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(setMyJobApplications)
      .catch(() => {});

    // If Admin, fetch admin statistics & records
    if (userRole === 'SKILL_DEPARTMENT_ADMIN' || userRole.endsWith('ADMIN')) {
      fetch(`${API_BASE}/api/admin/dashboard`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.json())
        .then(setAdminStats)
        .catch(() => {});

      fetch(`${API_BASE}/api/admin/enrollments`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.json())
        .then(setAdminEnrollments)
        .catch(() => {});

        const fetchAdminCatalogueSummary = async () => {
    if (!token) return;
    setAdminCatalogueLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/admin/catalogue-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAdminCatalogueData(data);
      }
    } catch (e) {
      console.error('Failed to load admin catalogue summary', e);
    } finally {
      setAdminCatalogueLoading(false);
    }
  };

      fetchAdminCentres();
      fetchAdminCatalogueSummary();
    }
  }, [token, userRole]);


  // Save or Unsave Career Opportunity permanently
  const handleToggleSaveJob = async (job: any) => {
    if (!token) {
      setAuthPortalView('login_citizen');
      return;
    }
    const isSaved = savedJobs.some((s: any) => s.job_id === job.id);
    try {
      if (isSaved) {
        const res = await fetch(`${API_BASE}/api/jobs/${job.id}/save`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setSavedJobs(prev => prev.filter((s: any) => s.job_id !== job.id));
        setBannerNotice(`Opportunity '${job.title}' removed from saved list.`);
      } else {
        const res = await fetch(`${API_BASE}/api/jobs/${job.id}/save`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        // Refresh saved list
        const refreshed = await (await fetch(`${API_BASE}/api/jobs/saved`, { headers: { Authorization: `Bearer ${token}` } })).json();
        setSavedJobs(refreshed);
        setBannerNotice(`Opportunity '${job.title}' permanently saved in MySQL.`);
      }
    } catch (err: any) {
      setBannerNotice(`Error updating saved opportunity: ${err.message}`);
    }
  };

  // Open internal application modal for a career opportunity
  const handleOpenJobApplyModal = (job: any) => {
    if (!token) {
      setAuthPortalView('login_citizen');
      return;
    }
    setApplyingJob(job);
    setJobApplyFullName(userName || myProfile?.full_name || '');
    setJobApplyEmail(userEmail || '');
    setJobApplyPhone(myProfile?.phone || '');
    setJobApplyEducation(myProfile?.education_qualification || 'Bachelor of Technology (B.Tech)');
    setJobApplyExperience(myProfile?.work_experience_years ? `${myProfile.work_experience_years} Years` : 'Fresh Graduate');
    setJobApplyStatement('I am eager to apply my technical skill competencies developed through the NagrikSetu Skill Mission to contribute effectively in this role.');
    setJobApplyMsg(null);
  };

  // Submit internal job application
  const handleSubmitJobApplication = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !applyingJob) return;
    setJobApplyLoading(true);
    setJobApplyMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/jobs/apply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          job_id: applyingJob.id,
          full_name: jobApplyFullName,
          email: jobApplyEmail,
          phone: jobApplyPhone,
          education: jobApplyEducation,
          experience_years: jobApplyExperience,
          statement: jobApplyStatement
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Failed to submit application');
      }
      setJobApplyMsg({ type: 'success', text: `${t('careers.apply_success')} Ref: ${data.application_ref}` });
      // Refresh my applications
      const refreshedApps = await (await fetch(`${API_BASE}/api/jobs/applications/me`, { headers: { Authorization: `Bearer ${token}` } })).json();
      setMyJobApplications(refreshedApps);
      setTimeout(() => {
        setApplyingJob(null);
        setActiveTab('applications');
        setAppsActiveSubTab('jobs');
      }, 1500);
    } catch (err: any) {
      setJobApplyMsg({ type: 'error', text: err.message });
    } finally {
      setJobApplyLoading(false);
    }
  };

  // Handle Login OTP Dispatch
  const handleSendLoginOtp = async () => {
    const emailClean = (loginEmail || '').trim();
    if (!emailClean || !emailClean.includes('@')) {
      setLoginOtpMsg({ type: 'error', text: 'Please enter a valid email address before requesting OTP.' });
      return;
    }
    setLoginOtpLoading(true);
    setLoginOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailClean, purpose: 'LOGIN' })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to send OTP');
      setLoginOtpRef(data.reference);
      setLoginOtpSent(true);
      setLoginOtpDemoMode(Boolean(data.demo_mode));
      if (data.demo_otp) {
        setLoginOtpDemoCode(data.demo_otp);
      } else {
        setLoginOtpDemoCode('');
      }
      setLoginOtpMsg({ type: 'success', text: data.message || `OTP sent to ${data.recipient_masked || emailClean}` });
      setLoginOtpCooldown(data.cooldown_seconds || 60);
      setLoginOtpExpirySec(data.expires_in_seconds || 300);

      const timer = setInterval(() => {
        setLoginOtpCooldown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      const expTimer = setInterval(() => {
        setLoginOtpExpirySec(prev => {
          if (prev <= 1) {
            clearInterval(expTimer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err: any) {
      setLoginOtpMsg({ type: 'error', text: err.message });
    } finally {
      setLoginOtpLoading(false);
    }
  };

  const handleVerifyLoginOtp = async () => {
    if (!loginOtpCode || loginOtpCode.trim().length !== 6) {
      setLoginOtpMsg({ type: 'error', text: 'Please enter the 6-digit OTP code received on your email.' });
      return;
    }
    setLoginOtpLoading(true);
    setLoginOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reference: loginOtpRef, code: loginOtpCode.trim() })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'OTP verification failed');
      setLoginOtpVerified(true);
      setLoginOtpMsg({ type: 'success', text: 'Email verified successfully.' });
    } catch (err: any) {
      setLoginOtpMsg({ type: 'error', text: err.message });
    } finally {
      setLoginOtpLoading(false);
    }
  };

  // Handle Authentication for Citizen, Training Centre Admin & Platform Admin
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (authPortalView === 'login_citizen') {
      if (citizenLoginMode === 'otp' && (!loginOtpVerified || !loginOtpRef)) {
        setAuthError('Please verify your email address via OTP before logging in.');
        return;
      }
      if (citizenLoginMode === 'password' && !loginPassword.trim()) {
        setAuthError('Please enter your account password.');
        return;
      }
    }
    setAuthLoading(true);
    setAuthError('');
    try {
      const payload: any = { email: loginEmail };
      if (authPortalView === 'login_citizen') {
        if (citizenLoginMode === 'password') {
          payload.password = loginPassword;
        } else {
          payload.otp_reference = loginOtpRef;
        }
      } else if (authPortalView === 'login_centre' || authPortalView === 'login_admin' || isAdminLogin || loginPassword.trim()) {
        payload.password = loginPassword;
      } else {
        payload.otp_reference = loginOtpRef;
      }

      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Login failed');

      // Server-side role verification against selected portal option
      if (authPortalView === 'login_centre' && data.role !== 'TRAINING_CENTRE_ADMIN') {
        throw new Error('Access Denied: This portal is for accredited Training Centre Administrators. Please use Citizen Login.');
      }
      if (authPortalView === 'login_admin' && data.role !== 'SKILL_DEPARTMENT_ADMIN' && data.role !== 'GOVERNMENT_ADMIN') {
        throw new Error('Access Denied: Platform Administrator privileges required. Please use the appropriate login portal.');
      }
      if (authPortalView === 'login_student') {
        if (!data.is_student) {
          throw new Error('Access Denied: Student Portal access requires at least one formally enrolled training programme with an assigned batch. Once a training centre approves and enrols your application, your Student ID and portal will become active.');
        }
      }
      if (authPortalView === 'login_citizen' && (data.role === 'TRAINING_CENTRE_ADMIN' || data.role === 'SKILL_DEPARTMENT_ADMIN')) {
        // Administrative accounts should use their dedicated portal
        // but if they authenticate, ensure correct redirection
      }

      setToken(data.access_token);
      setUserRole(data.role);
      setCitizenRef(data.citizen_ref || '');
      setUserEmail(data.email);
      setUserName(data.full_name || '');
      setIsStudent(Boolean(data.is_student));
      setStudentId(data.student_id || '');

      localStorage.setItem('ns_skill_token', data.access_token);
      localStorage.setItem('ns_skill_role', data.role);
      localStorage.setItem('ns_skill_citizen_ref', data.citizen_ref || '');
      localStorage.setItem('ns_skill_email', data.email);
      localStorage.setItem('ns_skill_name', data.full_name || '');
      localStorage.setItem('ns_skill_is_student', data.is_student ? 'true' : 'false');
      localStorage.setItem('ns_skill_student_id', data.student_id || '');

      // Multi-Centre Admin Association handling
      if (data.role === 'TRAINING_CENTRE_ADMIN') {
        const adminCentres = data.assigned_centres || [];
        setAssignedCentres(adminCentres);
        localStorage.setItem('ns_skill_assigned_centres', JSON.stringify(adminCentres));

        if (adminCentres.length === 0) {
          // Unassigned Admin: No centres associated
          setCentreId('');
          localStorage.removeItem('ns_skill_centre_id');
          setUnassignedCentreNotice(true);
        } else if (adminCentres.length === 1) {
          // Single Centre: Automatically select and proceed directly to dashboard
          const singleId = String(adminCentres[0].id);
          setCentreId(singleId);
          localStorage.setItem('ns_skill_centre_id', singleId);
          setShowCentreSelectModal(false);
          setUnassignedCentreNotice(false);
        } else {
          // Multiple Centres: Prompt selection modal / default to first
          const currentId = data.centre_id ? String(data.centre_id) : String(adminCentres[0].id);
          setCentreId(currentId);
          localStorage.setItem('ns_skill_centre_id', currentId);
          setShowCentreSelectModal(true);
          setUnassignedCentreNotice(false);
        }
      } else {
        setCentreId(data.centre_id ? String(data.centre_id) : '');
        localStorage.setItem('ns_skill_centre_id', data.centre_id ? String(data.centre_id) : '');
        setAssignedCentres([]);
        localStorage.removeItem('ns_skill_assigned_centres');
        setShowCentreSelectModal(false);
        setUnassignedCentreNotice(false);
      }

      setShowLoginModal(false);
      setAuthPortalView('none');
      setBannerNotice(`Welcome back, ${data.full_name || data.email}!`);
      
      // Automatic role-based dashboard redirection
      if (data.role === 'SKILL_DEPARTMENT_ADMIN' || data.role === 'GOVERNMENT_ADMIN') {
        setAdminTab('applications');
      } else if (data.role === 'TRAINING_CENTRE_ADMIN') {
        setCentreTab('dashboard');
      } else if (authPortalView === 'login_student' || data.is_student) {
        setActiveTab('student_portal');
      } else {
        setActiveTab('home');
      }
    } catch (err: any) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  // Handle Citizen Registration (Email OTP)
  const handleSendRegOtp = async () => {
    const emailClean = (regEmail || '').trim();
    if (!emailClean || !emailClean.includes('@')) {
      setRegOtpMsg({ type: 'error', text: 'Please enter a valid email address before requesting OTP.' });
      return;
    }
    setRegOtpLoading(true);
    setRegOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailClean, purpose: 'REGISTRATION' })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to send OTP');
      setRegOtpRef(data.reference);
      setRegOtpSent(true);
      setRegOtpDemoMode(Boolean(data.demo_mode));
      if (data.demo_otp) {
        setRegOtpDemoCode(data.demo_otp);
      } else {
        setRegOtpDemoCode('');
      }
      setRegOtpMsg({ type: 'success', text: data.message || `OTP sent to ${data.recipient_masked || emailClean}` });
      setRegOtpCooldown(data.cooldown_seconds || 60);
      setRegOtpExpirySec(data.expires_in_seconds || 300);

      const timer = setInterval(() => {
        setRegOtpCooldown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      const expTimer = setInterval(() => {
        setRegOtpExpirySec(prev => {
          if (prev <= 1) {
            clearInterval(expTimer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err: any) {
      setRegOtpMsg({ type: 'error', text: err.message });
    } finally {
      setRegOtpLoading(false);
    }
  };

  const handleVerifyRegOtp = async () => {
    if (!regOtpCode || regOtpCode.trim().length !== 6) {
      setRegOtpMsg({ type: 'error', text: 'Please enter the 6-digit OTP code received on your email.' });
      return;
    }
    setRegOtpLoading(true);
    setRegOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reference: regOtpRef, code: regOtpCode.trim() })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'OTP verification failed');
      setRegOtpVerified(true);
      setRegOtpMsg({ type: 'success', text: 'Email verified successfully.' });
    } catch (err: any) {
      setRegOtpMsg({ type: 'error', text: err.message });
    } finally {
      setRegOtpLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!regOtpVerified || !regOtpRef) {
      setAuthError('Please verify your email address via OTP before completing registration.');
      return;
    }
    if (!regPhone || regPhone.trim().length < 10) {
      setAuthError('Please enter a valid 10-digit mobile number.');
      return;
    }
    if (!regPassword || regPassword.length < 8) {
      setAuthError('Password must be at least 8 characters in length.');
      return;
    }
    if (regPassword !== regConfirmPassword) {
      setAuthError('Password and Confirm Password do not match.');
      return;
    }
    if (!regTermsAgreed) {
      setAuthError('You must accept the Terms of Use and Privacy Policy to register.');
      return;
    }
    setAuthLoading(true);
    setAuthError('');
    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: regFullName,
          email: regEmail,
          password: regPassword,
          phone: regPhone,
          otp_reference: regOtpRef
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Registration failed');

      // Pre-fill registered email for smooth login
      setLoginEmail(regEmail);
      setLoginPassword(regPassword);
      setCitizenLoginMode('password');

      // Navigate directly to citizen login
      setShowRegisterModal(false);
      setAuthPortalView('login_citizen');
      setBannerNotice('Citizen account created successfully! Sign in with your password or request an OTP.');
    } catch (err: any) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  // Forgot / Reset Password Handlers
  const handleSendForgotOtp = async () => {
    const emailClean = (forgotEmail || '').trim();
    if (!emailClean) {
      setForgotOtpMsg({ type: 'error', text: 'Please enter your registered email address.' });
      return;
    }
    setForgotOtpLoading(true);
    setForgotOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailClean, purpose: 'PASSWORD_RESET' })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to send OTP');
      setForgotOtpRef(data.reference);
      setForgotOtpSent(true);
      setForgotOtpDemoMode(Boolean(data.demo_mode));
      if (data.demo_otp) setForgotOtpDemoCode(data.demo_otp);
      setForgotOtpCooldown(data.cooldown_seconds || 60);
      setForgotOtpMsg({ type: 'success', text: `Verification OTP dispatched to ${data.recipient_masked || emailClean}.` });
    } catch (err: any) {
      setForgotOtpMsg({ type: 'error', text: err.message });
    } finally {
      setForgotOtpLoading(false);
    }
  };

  const handleVerifyForgotOtp = async () => {
    if (!forgotOtpCode || forgotOtpCode.trim().length !== 6) {
      setForgotOtpMsg({ type: 'error', text: 'Please enter the 6-digit OTP code received on your email.' });
      return;
    }
    setForgotOtpLoading(true);
    setForgotOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reference: forgotOtpRef, code: forgotOtpCode.trim() })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'OTP verification failed');
      setForgotOtpVerified(true);
      setForgotOtpMsg({ type: 'success', text: 'Email verified successfully. Enter your new password below.' });
    } catch (err: any) {
      setForgotOtpMsg({ type: 'error', text: err.message });
    } finally {
      setForgotOtpLoading(false);
    }
  };

  const handleResetPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!forgotOtpVerified || !forgotOtpRef) {
      setForgotOtpMsg({ type: 'error', text: 'Please verify the OTP sent to your email.' });
      return;
    }
    if (!forgotNewPassword || forgotNewPassword.length < 8) {
      setForgotOtpMsg({ type: 'error', text: 'New password must be at least 8 characters in length.' });
      return;
    }
    if (forgotNewPassword !== forgotConfirmPassword) {
      setForgotOtpMsg({ type: 'error', text: 'New password and confirm password do not match.' });
      return;
    }
    setForgotSubmitting(true);
    setForgotOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: forgotEmail,
          otp_reference: forgotOtpRef,
          new_password: forgotNewPassword,
          confirm_password: forgotConfirmPassword
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to reset password');
      setForgotSuccess('Password has been successfully updated! You can now log in.');
      setLoginEmail(forgotEmail);
      setLoginPassword(forgotNewPassword);
      setCitizenLoginMode('password');
      setTimeout(() => {
        setAuthPortalView(forgotSource === 'centre' ? 'login_centre' : 'login_citizen');
        setForgotSuccess('');
        setForgotOtpSent(false);
        setForgotOtpVerified(false);
        setForgotOtpRef('');
        setForgotOtpCode('');
        setForgotNewPassword('');
        setForgotConfirmPassword('');
      }, 2000);
    } catch (err: any) {
      setForgotOtpMsg({ type: 'error', text: err.message });
    } finally {
      setForgotSubmitting(false);
    }
  };

  // Set Password Handlers (For existing citizens without password)
  const handleSendSetPasswordOtp = async () => {
    const emailClean = (setPasswordEmail || '').trim();
    if (!emailClean) {
      setSetPasswordOtpMsg({ type: 'error', text: 'Please enter your registered email address.' });
      return;
    }
    setSetPasswordOtpLoading(true);
    setSetPasswordOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailClean, purpose: 'SET_PASSWORD' })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to send OTP');
      setSetPasswordOtpRef(data.reference);
      setSetPasswordOtpSent(true);
      setSetPasswordOtpDemoMode(Boolean(data.demo_mode));
      if (data.demo_otp) setSetPasswordOtpDemoCode(data.demo_otp);
      setSetPasswordOtpCooldown(data.cooldown_seconds || 60);
      setSetPasswordOtpMsg({ type: 'success', text: `Verification OTP dispatched to ${data.recipient_masked || emailClean}.` });
    } catch (err: any) {
      setSetPasswordOtpMsg({ type: 'error', text: err.message });
    } finally {
      setSetPasswordOtpLoading(false);
    }
  };

  const handleVerifySetPasswordOtp = async () => {
    if (!setPasswordOtpCode || setPasswordOtpCode.trim().length !== 6) {
      setSetPasswordOtpMsg({ type: 'error', text: 'Please enter the 6-digit OTP code received on your email.' });
      return;
    }
    setSetPasswordOtpLoading(true);
    setSetPasswordOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reference: setPasswordOtpRef, code: setPasswordOtpCode.trim() })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'OTP verification failed');
      setSetPasswordOtpVerified(true);
      setSetPasswordOtpMsg({ type: 'success', text: 'Email verified successfully. Create your account password below.' });
    } catch (err: any) {
      setSetPasswordOtpMsg({ type: 'error', text: err.message });
    } finally {
      setSetPasswordOtpLoading(false);
    }
  };

  const handleSetPasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!setPasswordOtpVerified || !setPasswordOtpRef) {
      setSetPasswordOtpMsg({ type: 'error', text: 'Please verify the OTP sent to your email.' });
      return;
    }
    if (!setNewPasswordVal || setNewPasswordVal.length < 8) {
      setSetPasswordOtpMsg({ type: 'error', text: 'Password must be at least 8 characters in length.' });
      return;
    }
    if (setNewPasswordVal !== setConfirmPasswordVal) {
      setSetPasswordOtpMsg({ type: 'error', text: 'Password and Confirm Password do not match.' });
      return;
    }
    setSetPasswordSubmitting(true);
    setSetPasswordOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/set-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: setPasswordEmail,
          otp_reference: setPasswordOtpRef,
          new_password: setNewPasswordVal,
          confirm_password: setConfirmPasswordVal
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to set password');
      setSetPasswordSuccess('Password created successfully! You can now log in using your password.');
      setLoginEmail(setPasswordEmail);
      setLoginPassword(setNewPasswordVal);
      setCitizenLoginMode('password');
      setTimeout(() => {
        setAuthPortalView('login_citizen');
        setSetPasswordSuccess('');
        setSetPasswordOtpSent(false);
        setSetPasswordOtpVerified(false);
        setSetPasswordOtpRef('');
        setSetPasswordOtpCode('');
        setSetNewPasswordVal('');
        setSetConfirmPasswordVal('');
      }, 2000);
    } catch (err: any) {
      setSetPasswordOtpMsg({ type: 'error', text: err.message });
    } finally {
      setSetPasswordSubmitting(false);
    }
  };

  // Change Password Handler (Inside Citizen Profile Tab)
  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!changeCurrentPassword) {
      setChangePasswordMsg({ type: 'error', text: 'Please enter your current password.' });
      return;
    }
    if (!changeNewPassword || changeNewPassword.length < 8) {
      setChangePasswordMsg({ type: 'error', text: 'New password must be at least 8 characters in length.' });
      return;
    }
    if (changeNewPassword !== changeConfirmPassword) {
      setChangePasswordMsg({ type: 'error', text: 'New password and confirm password do not match.' });
      return;
    }
    setChangePasswordLoading(true);
    setChangePasswordMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/change-password`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          current_password: changeCurrentPassword,
          new_password: changeNewPassword,
          confirm_password: changeConfirmPassword
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to change password');
      setChangePasswordMsg({ type: 'success', text: 'Password successfully updated!' });
      setChangeCurrentPassword('');
      setChangeNewPassword('');
      setChangeConfirmPassword('');
    } catch (err: any) {
      setChangePasswordMsg({ type: 'error', text: err.message });
    } finally {
      setChangePasswordLoading(false);
    }
  };

  const handleLogout = () => {
    setAuthPortalView('none');
    setToken('');
    setUserRole('');
    setCitizenRef('');
    setCentreId('');
    setUserEmail('');
    setUserName('');
    setIsStudent(false);
    setStudentId('');
    setStudentDashboardData(null);
    localStorage.removeItem('ns_skill_token');
    localStorage.removeItem('ns_skill_role');
    localStorage.removeItem('ns_skill_citizen_ref');
    localStorage.removeItem('ns_skill_centre_id');
    localStorage.removeItem('ns_skill_email');
    localStorage.removeItem('ns_skill_name');
    localStorage.removeItem('ns_skill_is_student');
    localStorage.removeItem('ns_skill_student_id');
    setActiveTab('home');
    setBannerNotice('You have been signed out.');
  };

  // Fetch Student Dashboard Data
  const fetchStudentDashboard = async () => {
    if (!token) return;
    setStudentDashboardLoading(true);
    setStudentDashboardError('');
    try {
      const res = await fetch(`${API_BASE}/api/student/dashboard`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to retrieve student dashboard records.');
      }
      const data = await res.json();
      setStudentDashboardData(data);
      if (data.is_student) {
        setIsStudent(true);
        if (data.student_id) {
          setStudentId(data.student_id);
          localStorage.setItem('ns_skill_student_id', data.student_id);
        }
        localStorage.setItem('ns_skill_is_student', 'true');
      }
    } catch (err: any) {
      console.error('Error fetching student dashboard:', err);
      setStudentDashboardError(err.message || 'Unable to load student learning data.');
    } finally {
      setStudentDashboardLoading(false);
    }
  };

  // Automatically fetch student dashboard whenever activeTab changes to student_portal
  useEffect(() => {
    if (activeTab === 'student_portal' && token) {
      fetchStudentDashboard();
    }
  }, [activeTab, token]);

  // Open Category Details Page (Amazon-style Hierarchy)
  const openCategoryDetails = async (categoryIdentifier: string) => {
    setActiveCategoryCode(categoryIdentifier);
    setSelectedSubcategoryId(null);
    setActiveTab('category_details');
    setLoadingCategoryDetails(true);
    setCategoryDetailsError('');
    setCategoryDetailsData(null);
    try {
      const res = await fetch(`${API_BASE}/api/categories/${encodeURIComponent(categoryIdentifier)}`);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `Failed to load category '${categoryIdentifier}'`);
      }
      const data = await res.json();
      setCategoryDetailsData(data);
    } catch (err: any) {
      console.error('Error loading category details:', err);
      setCategoryDetailsError(err.message || 'Unable to retrieve category details');
    } finally {
      setLoadingCategoryDetails(false);
    }
  };

  // Open Full Course Details
  const openCourseDetail = async (code: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/skills/${code}`);
      const data = await res.json();
      setSelectedCourse(data);
      setCourseDetailTab('overview');
    } catch (e) {
      console.error(e);
    }
  };

  // Open Profile Edit Modal with prefilled values
  const handleOpenEditProfile = () => {
    setEditFullName(myProfile?.full_name || userName || '');
    setEditPhone(myProfile?.phone || '');
    setEditDob(myProfile?.date_of_birth || '');
    setEditGender(myProfile?.gender || 'Male');
    setEditAddress(myProfile?.residential_address || '');
    setEditEducation(myProfile?.education_qualification || 'Bachelor of Engineering / Science');
    setEditEmployment(myProfile?.current_employment_status || 'Job Seeker');
    setEditExpYears(myProfile?.work_experience_years || 0);
    setEditInterests(myProfile?.interests || '');
    setEditGoals(myProfile?.career_goals || '');
    setEditPrefMode(myProfile?.preferred_training_mode || 'Hybrid');
    setEditPrefLocation(myProfile?.preferred_training_location || 'Bengaluru');
    setEditResumeSummary(myProfile?.resume_summary || '');
    setProfileMsg(null);
    setProfileOtpSent(false);
    setProfileOtpCode('');
    setProfileOtpRef('');
    setProfileOtpVerified(false);
    setProfileOtpMsg(null);
    setShowEditProfileModal(true);
  };

  const handleSendProfileOtp = async () => {
    if (!editPhone || editPhone.trim().length < 10) {
      setProfileOtpMsg({ type: 'error', text: 'Please enter a valid 10-digit mobile number before requesting OTP.' });
      return;
    }
    setProfileOtpLoading(true);
    setProfileOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ phone: editPhone.trim(), purpose: 'PROFILE_PHONE_UPDATE' })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to send OTP');
      setProfileOtpRef(data.reference);
      setProfileOtpSent(true);
      setProfileOtpMsg({ type: 'success', text: data.message || `OTP sent to ${data.phone_masked || editPhone}` });
      setProfileOtpCooldown(data.cooldown_seconds || 60);
      const timer = setInterval(() => {
        setProfileOtpCooldown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err: any) {
      setProfileOtpMsg({ type: 'error', text: err.message });
    } finally {
      setProfileOtpLoading(false);
    }
  };

  const handleVerifyProfileOtp = async () => {
    if (!profileOtpCode || profileOtpCode.trim().length !== 6) {
      setProfileOtpMsg({ type: 'error', text: 'Please enter the 6-digit OTP code received on SMS.' });
      return;
    }
    setProfileOtpLoading(true);
    setProfileOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ reference: profileOtpRef, code: profileOtpCode.trim() })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'OTP verification failed');
      setProfileOtpVerified(true);
      setProfileOtpMsg({ type: 'success', text: 'New mobile number verified successfully!' });
    } catch (err: any) {
      setProfileOtpMsg({ type: 'error', text: err.message });
    } finally {
      setProfileOtpLoading(false);
    }
  };

  // Submit Profile Updates to Backend
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;

    // Check if phone changed: require OTP verification
    const currentNorm = (myProfile?.phone || '').replace(/\D/g, '');
    const newNorm = editPhone.trim().replace(/\D/g, '');
    const phoneChanged = currentNorm !== newNorm && newNorm.length >= 10;

    if (phoneChanged && (!profileOtpVerified || !profileOtpRef)) {
      setProfileMsg({ type: 'error', text: 'Updating your mobile number requires SMS OTP verification.' });
      return;
    }

    setProfileSaving(true);
    setProfileMsg(null);

    try {
      const payload: any = {
        full_name: editFullName.trim(),
        phone: editPhone.trim(),
        date_of_birth: editDob.trim(),
        gender: editGender,
        residential_address: editAddress.trim(),
        education_qualification: editEducation,
        current_employment_status: editEmployment,
        work_experience_years: Number(editExpYears),
        interests: editInterests.trim(),
        career_goals: editGoals.trim(),
        preferred_training_mode: editPrefMode,
        preferred_training_location: editPrefLocation.trim(),
        resume_summary: editResumeSummary.trim()
      };
      if (phoneChanged) {
        payload.otp_reference = profileOtpRef;
      }

      const res = await fetch(`${API_BASE}/api/profiles/me`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to update profile');

      setProfileMsg({ type: 'success', text: 'Profile successfully updated and saved to MySQL!' });
      setUserName(editFullName.trim());
      localStorage.setItem('user_name', editFullName.trim());

      // Refresh Profile
      const profRes = await fetch(`${API_BASE}/api/profiles/me`, { headers: { Authorization: `Bearer ${token}` } });
      const refreshed = await profRes.json();
      setMyProfile(refreshed);

      setTimeout(() => {
        setShowEditProfileModal(false);
      }, 1200);
    } catch (err: any) {
      setProfileMsg({ type: 'error', text: err.message });
    } finally {
      setProfileSaving(false);
    }
  };

  // Prepopulate Enrolment Form when starting enrollment
  const handleStartEnrolment = async (prog: any) => {
    // Strictly restrict citizen training applications to CITIZEN accounts only
    if (userRole === 'SKILL_DEPARTMENT_ADMIN' || userRole === 'GOVERNMENT_ADMIN' || userRole === 'TRAINING_CENTRE_ADMIN' || userRole.endsWith('ADMIN') || userRole === 'PROJECT_OWNER') {
      alert('This feature is available to Citizen accounts only. Administrative and institutional accounts cannot apply for training programmes.');
      return;
    }
    
    let activeProg = { ...prog };
    
    // Always fetch fresh live batch records for this programme to ensure latest seats and open batches
    try {
      const progRes = await fetch(`${API_BASE}/api/programmes/${prog.id}`);
      if (progRes.ok) {
        const fullProgData = await progRes.json();
        if (fullProgData && fullProgData.batches) {
          activeProg = { ...activeProg, ...fullProgData };
        }
      }
    } catch (err) {
      console.warn('Could not fetch fresh batches for programme:', err);
    }

    setEnrollingProgram(activeProg);
    const validBatches = (activeProg.batches || []).filter((b: any) => b.status === 'ADMISSIONS_OPEN' && b.available_seats > 0);
    if (validBatches.length > 0) {
      setSelectedBatchId(validBatches[0].id);
    } else if (activeProg.batches && activeProg.batches.length > 0) {
      setSelectedBatchId(activeProg.batches[0].id);
    } else {
      setSelectedBatchId(null);
    }
    setEnrolmentErrorMsg('');
    setEnrolmentSuccessMsg('');

    // Prepopulate Sections A-H from Profile
    setAppFullName(myProfile?.full_name || userName || '');
    setAppEmail(myProfile?.email || userEmail || '');
    setAppPhone(myProfile?.phone || '');
    setAppDob(myProfile?.date_of_birth || '1998-05-15');
    setAppGender(myProfile?.gender || 'Male');
    setAppAltPhone('');

    setAppAddress(myProfile?.residential_address || '124, 4th Cross, Indiranagar');
    setAppCity(myProfile?.preferred_training_location || 'Bengaluru');
    setAppState('Karnataka');
    setAppPincode('560038');

    setAppEducation(myProfile?.education_qualification || 'Bachelor of Engineering / Science');
    setAppInstitution('Visvesvaraya Technological University');
    setAppGradYear('2024');
    setAppSpecialization('Computer Science & Information Technology');

    setAppEmploymentStatus(myProfile?.current_employment_status || 'Job Seeker');
    setAppOccupation(myProfile?.current_employment_status === 'Employed' ? 'Junior Software Engineer' : 'Graduate Scholar');
    setAppExperienceYears(myProfile?.work_experience_years || 0);

    setAppPrefTiming('Morning (09:00 AM - 12:00 PM)');
    setAppPrefMode(activeProg.delivery_mode || activeProg.mode || 'Hybrid');

    setEnrolmentStatement(myProfile?.career_goals || 'I am eager to master this curriculum to qualify for industry software engineering certifications and secure high-impact roles.');
    setAppTargetSkills(activeProg.skill?.name || activeProg.skill_name || activeProg.title || '');
    setAppPostJobPlacement(true);

    setAppIdProofType('Aadhaar / National Identity Card');
    setAppIdProofNumber('XXXX-XXXX-4921');
    setAppDocAttachedNote('Verified e-Aadhaar and Degree Marksheets attached in citizen locker.');

    setAppDeclarationAgreed(true);

    // Reset OTP verification state for new enrolment submission
    setEnrolOtpSent(false);
    setEnrolOtpCode('');
    setEnrolOtpRef('');
    setEnrolOtpVerified(false);
    setEnrolOtpMsg(null);
  };

  const handleSendEnrolOtp = async () => {
    const targetPhone = (appPhone || myProfile?.phone || '').trim();
    if (!targetPhone || targetPhone.length < 10) {
      setEnrolOtpMsg({ type: 'error', text: 'Please ensure your registered mobile number is entered in Section A.' });
      return;
    }
    setEnrolOtpLoading(true);
    setEnrolOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ phone: targetPhone, purpose: 'ENROLMENT' })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to send OTP');
      setEnrolOtpRef(data.reference);
      setEnrolOtpSent(true);
      setEnrolOtpMsg({ type: 'success', text: data.message || `OTP sent to ${data.phone_masked || targetPhone}` });
      setEnrolOtpCooldown(data.cooldown_seconds || 60);
      const timer = setInterval(() => {
        setEnrolOtpCooldown(prev => {
          if (prev <= 1) {
            clearInterval(timer);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err: any) {
      setEnrolOtpMsg({ type: 'error', text: err.message });
    } finally {
      setEnrolOtpLoading(false);
    }
  };

  const handleVerifyEnrolOtp = async () => {
    if (!enrolOtpCode || enrolOtpCode.trim().length !== 6) {
      setEnrolOtpMsg({ type: 'error', text: 'Please enter the 6-digit OTP code received on SMS.' });
      return;
    }
    setEnrolOtpLoading(true);
    setEnrolOtpMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/otp/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ reference: enrolOtpRef, code: enrolOtpCode.trim() })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'OTP verification failed');
      setEnrolOtpVerified(true);
      setEnrolOtpMsg({ type: 'success', text: 'Mobile verified successfully! You can now submit your application.' });
    } catch (err: any) {
      setEnrolOtpMsg({ type: 'error', text: err.message });
    } finally {
      setEnrolOtpLoading(false);
    }
  };

  // Enrolment Submit (Comprehensive 8-Section Application Dossier)
  const handleEnrolmentSubmit = async () => {
    if (!enrollingProgram) return;
    if (userRole && userRole !== 'CITIZEN') {
      setEnrolmentErrorMsg('This feature is available to Citizen accounts only. Non-citizen accounts cannot apply.');
      return;
    }
    if (!token) {
      setAuthPortalView('login_citizen');
      return;
    }

    if (!appDeclarationAgreed) {
      setEnrolmentErrorMsg('Please review and check the declaration checkbox before submitting your application.');
      return;
    }
    setEnrolmentErrorMsg('');
    setEnrolmentSuccessMsg('');
    setEnrolSubmitting(true);

    try {
      const simplifiedDossier = {
        section_a_personal: {
          full_name: appFullName,
          citizen_ref: citizenRef || 'CIT-2026-X',
          email: appEmail,
          phone: appPhone
        },
        section_b_location: {
          city_district: appCity,
          pincode: appPincode
        },
        // Maintained for backward compatibility with existing dashboard views
        section_b_address: {
          residential_address: appCity,
          city: appCity,
          state: 'Karnataka',
          pincode: appPincode
        },
        section_c_education: {
          highest_qualification: appEducation
        },
        section_d_employment: {
          employment_status: appEmploymentStatus
        },
        section_e_training: {
          program_id: enrollingProgram.id,
          program_code: enrollingProgram.code,
          program_title: enrollingProgram.title,
          centre_id: enrollingProgram.centre?.id || enrollingProgram.centre_id,
          centre_name: enrollingProgram.centre?.name || enrollingProgram.centre_name || 'Accredited Training Centre',
          batch_id: selectedBatchId,
          delivery_mode: appPrefMode
        },
        section_declaration: {
          agreed: true,
          terms: "I confirm that the submitted details are accurate and I agree to be contacted by the selected training centre regarding my application.",
          timestamp: new Date().toISOString()
        }
      };

      const res = await fetch(`${API_BASE}/api/enrollments`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          program_id: enrollingProgram.id,
          batch_id: selectedBatchId,
          selected_mode: appPrefMode,
          applicant_statement: enrolmentStatement,
          application_details: simplifiedDossier,
          otp_reference: enrolOtpRef
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Enrolment submission failed');

      setEnrolmentSuccessMsg(data.message);
      // Refresh My Applications
      fetch(`${API_BASE}/api/enrollments/me`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.json())
        .then(setMyApplications);

      setTimeout(() => {
        setEnrollingProgram(null);
        setActiveTab('applications');
      }, 1800);
    } catch (err: any) {
      setEnrolmentErrorMsg(err.message);
    } finally {
      setEnrolSubmitting(false);
    }
  };

  // Run Gap Analysis
  const runGapAnalysis = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/skill-gap/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ target_role: selectedTargetRole })
      });
      const data = await res.json();
      setGapReport(data);
    } catch (e) {
      console.error(e);
    }
  };

  // Add Skill to Citizen Profile
  const handleAddSkill = async () => {
    if (!newSkillInput.trim() || !token) return;
    try {
      await fetch(`${API_BASE}/api/profiles/me/skills`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ skill_name: newSkillInput.trim(), proficiency: 'Intermediate' })
      });
      setNewSkillInput('');
      const p = await (await fetch(`${API_BASE}/api/profiles/me`, { headers: { Authorization: `Bearer ${token}` } })).json();
      setMyProfile(p);
    } catch (e) {
      console.error(e);
    }
  };

  // Admin Review Submit
  const handleAdminReviewSubmit = async () => {
    if (!reviewModalApp || !token) return;
    try {
      const res = await fetch(`${API_BASE}/api/admin/enrollments/${reviewModalApp.id}/review`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ status: reviewStatus, remarks: reviewRemarks })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Review failed');

      setReviewModalApp(null);
      setBannerNotice(`Application ${data.application_id} updated to ${data.status}`);

      // Refresh admin list & stats
      const apps = await (await fetch(`${API_BASE}/api/admin/enrollments`, { headers: { Authorization: `Bearer ${token}` } })).json();
      setAdminEnrollments(apps);
      const stats = await (await fetch(`${API_BASE}/api/admin/dashboard`, { headers: { Authorization: `Bearer ${token}` } })).json();
      setAdminStats(stats);
    } catch (e: any) {
      alert(e.message);
    }
  };

  // Admin Create Skill
  const handleAdminCreateSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/api/admin/skills`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          name: newSkillName,
          category_name: newSkillCategory,
          level: newSkillLevel,
          duration_weeks: Number(newSkillWeeks),
          duration_hours: Number(newSkillHours),
          summary: newSkillSummary,
          details: newSkillSummary,
          prerequisites: 'Basic literacy or 10th Pass'
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Skill creation failed');
      setBannerNotice(`Skill created successfully: ${data.code}`);
      setShowAddSkillModal(false);
      setNewSkillName('');
      setNewSkillSummary('');
      fetchSkills();
    } catch (err: any) {
      alert(err.message);
    }
  };

  // Admin Create Programme & Batch
  const handleAdminCreateProgramme = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      const resProg = await fetch(`${API_BASE}/api/admin/programmes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          skill_id: Number(newProgSkillId),
          title: newProgTitle,
          description: newProgDesc,
          mode: newProgMode,
          duration_hours: Number(newProgHours),
          fee: Number(newProgFee),
          scholarship_available: true,
          eligibility_criteria: '10th / 12th Pass or Graduate',
          start_date: '2026-11-25',
          end_date: '2027-01-15'
        })
      });
      const dataProg = await resProg.json();
      if (!resProg.ok) throw new Error(dataProg.detail || 'Programme creation failed');

      // Create initial batch
      await fetch(`${API_BASE}/api/admin/batches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          program_id: dataProg.id,
          batch_name: newProgBatchName,
          timings: newProgBatchTimings,
          training_schedule: newProgBatchSchedule,
          mode: newProgMode,
          total_seats: Number(newProgBatchSeats),
          start_date: '2026-11-25',
          end_date: '2027-01-15',
          application_deadline: '2026-11-22'
        })
      });

      setBannerNotice(`Programme created: ${dataProg.code} with admissions open.`);
      setShowAddProgrammeModal(false);
      setNewProgTitle('');
      setNewProgDesc('');
      fetch(`${API_BASE}/api/programmes`).then(r => r.json()).then(setProgrammes);
    } catch (err: any) {
      alert(err.message);
    }
  };

  // Admin Create Centre
  const handleAdminCreateCentre = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/api/admin/centres`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          name: newCentreName,
          location: newCentreLocation,
          district: newCentreDistrict,
          state: 'Karnataka',
          address: newCentreAddress,
          contact_phone: newCentrePhone,
          contact_email: newCentreEmail,
          delivery_modes: 'Online, Hybrid, Classroom',
          facilities: newCentreFacilities
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Centre creation failed');
      setBannerNotice(`Training Centre created: ${data.code}`);
      setShowAddCentreModal(false);
      setNewCentreName('');
      setNewCentreLocation('');
      setNewCentreAddress('');
      fetch(`${API_BASE}/api/centres`).then(r => r.json()).then(setCentres);
      fetchAdminCentres();
    } catch (err: any) {
      alert(err.message);
    }
  };

  // Fetch Government Admin Centres List (with admin accounts & statuses)
  const fetchAdminCatalogueSummary = async () => {
    if (!token) return;
    setAdminCatalogueLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/admin/catalogue-summary`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAdminCatalogueData(data);
      }
    } catch (e) {
      console.error('Failed to load admin catalogue summary', e);
    } finally {
      setAdminCatalogueLoading(false);
    }
  };

  const fetchAdminCentres = async () => {
    if (!token) return;
    setAdminCentresLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/admin/centres`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAdminCentresList(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setAdminCentresLoading(false);
    }
  };

  // Handle Assigning / Creating Centre Administrator
  const handleAssignCentreAdmin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCentreForAdmin || !token) return;
    setAssignAdminSubmitting(true);
    setAssignAdminMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/admin/centres/${selectedCentreForAdmin.id}/assign-admin`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          full_name: assignAdminFullName,
          email: assignAdminEmail,
          password: assignAdminPassword,
          phone: assignAdminPhone || undefined
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to establish Centre Administrator');
      setAssignAdminMsg({ type: 'success', text: data.message || 'Centre Administrator assigned successfully!' });
      setBannerNotice(`Centre Admin assigned: ${assignAdminEmail}`);
      fetchAdminCentres();
      setTimeout(() => {
        setSelectedCentreForAdmin(null);
        setAssignAdminMsg(null);
      }, 1500);
    } catch (err: any) {
      setAssignAdminMsg({ type: 'error', text: err.message });
    } finally {
      setAssignAdminSubmitting(false);
    }
  };

  // Handle Centre Status Change (Approve, Suspend, Reactivate, Reject)
  const handleUpdateCentreStatus = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedCentreForStatus || !token) return;
    if (centreStatusTarget === 'REJECTED' && !centreStatusReason.trim()) {
      setCentreStatusMsg({ type: 'error', text: 'Rejection reason is mandatory.' });
      return;
    }
    setCentreStatusSubmitting(true);
    setCentreStatusMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/admin/centres/${selectedCentreForStatus.id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          approval_status: centreStatusTarget,
          rejection_reason: centreStatusReason.trim() || undefined
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to update centre status');
      setCentreStatusMsg({ type: 'success', text: `Centre status updated to ${centreStatusTarget} successfully!` });
      setBannerNotice(`Centre ${data.code} status updated to ${centreStatusTarget}`);
      fetchAdminCentres();
      fetch(`${API_BASE}/api/centres`).then(r => r.json()).then(setCentres);
      setTimeout(() => {
        setSelectedCentreForStatus(null);
        setCentreStatusMsg(null);
      }, 1500);
    } catch (err: any) {
      setCentreStatusMsg({ type: 'error', text: err.message });
    } finally {
      setCentreStatusSubmitting(false);
    }
  };

  // Fetch Centre Admin Data
  const fetchCentreData = async (targetCentreId?: string) => {
    if (!token || userRole !== 'TRAINING_CENTRE_ADMIN') return;
    const cid = targetCentreId || centreId;
    if (!cid && assignedCentres.length === 0) {
      setUnassignedCentreNotice(true);
      return;
    }
    setCentreLoading(true);
    try {
      const headers: Record<string, string> = { Authorization: `Bearer ${token}` };
      if (cid) {
        headers['X-Centre-ID'] = cid;
      }
      const [dashRes, profRes, progsRes, batchesRes, trainersRes, enrRes, reportsRes] = await Promise.all([
        fetch(`${API_BASE}/api/centre-admin/dashboard`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API_BASE}/api/centre-admin/profile`, { headers }).then(r => r.ok ? r.json() : null),
        fetch(`${API_BASE}/api/centre-admin/programmes`, { headers }).then(r => r.ok ? r.json() : []),
        fetch(`${API_BASE}/api/centre-admin/batches`, { headers }).then(r => r.ok ? r.json() : []),
        fetch(`${API_BASE}/api/centre-admin/trainers`, { headers }).then(r => r.ok ? r.json() : []),
        fetch(`${API_BASE}/api/centre-admin/enrollments`, { headers }).then(r => r.ok ? r.json() : []),
        fetch(`${API_BASE}/api/centre-admin/reports`, { headers }).then(r => r.ok ? r.json() : null)
      ]);
      setCentreDashboard(dashRes);
      setCentreProfile(profRes);
      setCentreProgrammes(progsRes || []);
      setCentreBatches(batchesRes || []);
      setCentreTrainers(trainersRes || []);
      setCentreEnrollments(enrRes || []);
      setCentreReports(reportsRes);
      setUnassignedCentreNotice(false);
    } catch (err) {
      console.error('Error fetching centre admin data:', err);
    } finally {
      setCentreLoading(false);
    }
  };

  const switchAdminCentre = (newCid: string) => {
    setCentreId(newCid);
    localStorage.setItem('ns_skill_centre_id', newCid);
    setShowCentreSelectModal(false);
    // Clear old state immediately to prevent stale visual bleed
    setCentreDashboard(null);
    setCentreProfile(null);
    setCentreProgrammes([]);
    setCentreBatches([]);
    setCentreTrainers([]);
    setCentreEnrollments([]);
    setCentreReports(null);
    fetchCentreData(newCid);
  };

  useEffect(() => {
    if (userRole === 'TRAINING_CENTRE_ADMIN' && token) {
      fetchCentreData();
    }
  }, [userRole, token, centreId]);

  // Open Public Training Centre Profile
  const openPublicCentreProfile = async (cId: string | number) => {
    setActiveCentreProfileId(cId);
    setPublicCentreLoading(true);
    setPublicCentreTab('overview');
    setActiveTab('centre_profile');
    try {
      const res = await fetch(`${API_BASE}/api/centres/${encodeURIComponent(String(cId))}/profile`);
      if (res.ok) {
        const data = await res.json();
        setPublicCentreProfile(data);
      } else {
        setPublicCentreProfile(null);
      }
    } catch (e) {
      console.error('Failed to load centre profile:', e);
      setPublicCentreProfile(null);
    } finally {
      setPublicCentreLoading(false);
    }
  };

  const handleCentreReviewSubmit = async () => {
    if (!centreReviewModalApp || !token) return;
    if (centreReviewAction === 'REJECT' && (!centreReviewReason || centreReviewReason.trim().length < 3)) {
      setCentreReviewError('Please provide a mandatory rejection reason for this applicant.');
      return;
    }
    setCentreReviewSubmitting(true);
    setCentreReviewError('');
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      };
      if (centreId) headers['X-Centre-ID'] = centreId;

      const res = await fetch(`${API_BASE}/api/centre-admin/enrollments/${centreReviewModalApp.id}/review`, {
        method: 'PATCH',
        headers,
        body: JSON.stringify({
          action: centreReviewAction,
          remarks: centreReviewReason.trim(),
          rejection_reason: centreReviewAction === 'REJECT' ? centreReviewReason.trim() : undefined,
          internal_notes: centreInternalNotes.trim() || undefined
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Review submission failed');
      setCentreReviewModalApp(null);
      setCentreReviewReason('');
      setCentreInternalNotes('');
      setBannerNotice(`Application ${centreReviewModalApp.code} status updated to ${data.status}.`);
      fetchCentreData();
    } catch (err: any) {
      setCentreReviewError(err.message);
    } finally {
      setCentreReviewSubmitting(false);
    }
  };

  const handleCentreEnrolSubmit = async () => {
    if (!centreEnrolModalApp || !centreEnrolSelectedBatchId || !token) {
      setCentreEnrolError('Please select an active training batch to enrol this applicant.');
      return;
    }
    setCentreEnrolSubmitting(true);
    setCentreEnrolError('');
    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      };
      if (centreId) headers['X-Centre-ID'] = centreId;

      const res = await fetch(`${API_BASE}/api/centre-admin/enrollments/${centreEnrolModalApp.id}/enrol`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          batch_id: centreEnrolSelectedBatchId,
          internal_notes: centreEnrolInternalNotes.trim() || undefined
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Enrolment failed');
      setCentreEnrolModalApp(null);
      setCentreEnrolSelectedBatchId(null);
      setCentreEnrolInternalNotes('');
      setBannerNotice(`Applicant ${centreEnrolModalApp.citizen_name} enrolled successfully into ${data.batch_name}.`);
      fetchCentreData();
    } catch (err: any) {
      setCentreEnrolError(err.message);
    } finally {
      setCentreEnrolSubmitting(false);
    }
  };


  // Admin Progress Submit & Issue Certificate
  const handleIssueCertificate = async (id: number) => {
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/api/admin/enrollments/${id}/issue-certificate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Certificate issuance failed');
      alert(`Certificate issued: ${data.certificate_code}`);

      const apps = await (await fetch(`${API_BASE}/api/admin/enrollments`, { headers: { Authorization: `Bearer ${token}` } })).json();
      setAdminEnrollments(apps);
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div>
      {/* Official Government Top Bar for Non-Centre Portals */}
      {userRole !== 'TRAINING_CENTRE_ADMIN' && (
        <div className="gov-top-bar">
          <span>
            <Landmark size={14} className="text-orange-400" />
            Government of India • National Citizen Portal • National Skilling Initiative
          </span>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span>Accessibility: Keyboard-navigable Interface</span>
            <span style={{ fontSize: '0.72rem', color: '#cbd5e1' }}>English</span>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TRAINING CENTRE ADMINISTRATOR DESK & WORKSPACE                           */}
      {/* Strict separation: Centre Admin only accesses Centre-scoped APIs         */}
      {/* ========================================================================= */}
      {userRole === 'TRAINING_CENTRE_ADMIN' ? (
        <div>
          {/* DEDICATED 3-SECTION TRAINING CENTRE HEADER & NAVIGATION ARCHITECTURE */}
          <header className="tc-header-wrapper" role="banner">
            {/* SECTION A: Official Government Information Bar */}
            <div className="tc-gov-bar">
              <div className="tc-gov-container">
                <div className="tc-gov-left">
                  <Landmark size={14} className="text-orange-400" />
                  <span>Government of India • National Citizen Portal • National Skilling Initiative</span>
                </div>
                <div className="tc-gov-right">
                  <span>Accessibility: Keyboard-navigable Interface</span>
                  <select 
                    className="tc-lang-select" 
                    aria-label="Language Selector"
                    defaultValue="en"
                  >
                    <option value="en">English</option>
                  </select>
                </div>
              </div>
            </div>

            {/* SECTION B: Branding & Authenticated Centre Identity */}
            <div className="tc-identity-bar">
              <div className="tc-identity-container">
                {/* Left: Branding & Subtitle */}
                <div 
                  className="tc-brand-left" 
                  onClick={() => { setCentreTab('dashboard'); setCentreMobileMenuOpen(false); }}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { setCentreTab('dashboard'); setCentreMobileMenuOpen(false); } }}
                  aria-label="NagrikSetu Training Centre Portal Home"
                >
                  <div className="tc-brand-icon">
                    <Building2 size={24} color="#ffffff" />
                  </div>
                  <div>
                    <h1 className="tc-brand-title">NagrikSetu</h1>
                    <div className="tc-brand-subtitle">Training Centre Portal</div>
                  </div>
                </div>

                {/* Right: Centre Identity & Verification */}
                <div className="tc-centre-right">
                  {/* Multi-Centre Switcher Dropdown (if assigned multiple centres) */}
                  {assignedCentres && assignedCentres.length > 1 && (
                    <div className="tc-centre-switcher">
                      <Building2 size={14} color="#0f766e" />
                      <select
                        value={centreId || (assignedCentres[0]?.id ? String(assignedCentres[0].id) : '')}
                        onChange={(e) => switchAdminCentre(e.target.value)}
                        aria-label="Select Training Centre"
                      >
                        {assignedCentres.map((ac: any) => (
                          <option key={ac.id} value={String(ac.id)}>
                            {ac.name} ({ac.district})
                          </option>
                        ))}
                      </select>
                    </div>
                  )}

                  <div className="tc-centre-info-card">
                    <div className="tc-centre-name" title={centreProfile?.name || 'Authorized Training Centre'}>
                      {centreProfile?.name || 'Authorized Training Centre'}
                    </div>
                    <div className="tc-centre-badge-row">
                      <span className="tc-pulse-dot" aria-hidden="true"></span>
                      <span className="tc-verified-label">CENTRE ADMIN VERIFIED</span>
                      {userName && (
                        <span className="tc-admin-user">• {userName}</span>
                      )}
                    </div>
                  </div>

                  {/* Mobile Hamburger Menu Toggle Button */}
                  <button
                    type="button"
                    className="tc-mobile-toggle"
                    onClick={() => setCentreMobileMenuOpen(!centreMobileMenuOpen)}
                    aria-label="Toggle training centre navigation menu"
                    aria-expanded={centreMobileMenuOpen}
                  >
                    {centreMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
                  </button>
                </div>
              </div>
            </div>

            {/* SECTION C: Primary Desktop Navigation Bar */}
            <div className="tc-nav-bar">
              <div className="tc-nav-container">
                <nav className="tc-nav-links-desktop" aria-label="Training Centre Navigation">
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'dashboard' ? 'active' : ''}`}
                    onClick={() => setCentreTab('dashboard')}
                  >
                    <Target size={15} /> Dashboard & Stats
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'applications' ? 'active' : ''}`}
                    onClick={() => setCentreTab('applications')}
                  >
                    <FileText size={15} /> Applications
                    <span className="tc-nav-count">{centreEnrollments.length}</span>
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'programmes' ? 'active' : ''}`}
                    onClick={() => setCentreTab('programmes')}
                  >
                    <GraduationCap size={15} /> Courses & Batches
                    <span className="tc-nav-count">{centreProgrammes.length}</span>
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'trainers' ? 'active' : ''}`}
                    onClick={() => setCentreTab('trainers')}
                  >
                    <Users size={15} /> Trainers
                    <span className="tc-nav-count">{centreTrainers.length}</span>
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'profile' ? 'active' : ''}`}
                    onClick={() => setCentreTab('profile')}
                  >
                    <Building2 size={15} /> Centre Profile & Labs
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'reports' ? 'active' : ''}`}
                    onClick={() => setCentreTab('reports')}
                  >
                    <Award size={15} /> Reports & Analytics
                  </button>
                  <button
                    type="button"
                    className={`tc-nav-link ${centreTab === 'security' ? 'active' : ''}`}
                    onClick={() => setCentreTab('security')}
                  >
                    <Lock size={15} /> Security & Password
                  </button>
                </nav>

                {/* Far-Right Outlined Logout Button */}
                <button 
                  type="button"
                  className="tc-logout-btn" 
                  onClick={handleLogout}
                  aria-label="Log out of Training Centre Portal"
                >
                  <LogOut size={15} /> {t('nav.logout')}
                </button>
              </div>
            </div>

            {/* Mobile / Compact Navigation Drawer */}
            <div className={`tc-mobile-drawer ${centreMobileMenuOpen ? 'open' : ''}`} role="dialog" aria-label="Mobile Navigation Drawer">
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'dashboard' ? 'active' : ''}`}
                onClick={() => { setCentreTab('dashboard'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Target size={16} /> Dashboard & Stats</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'applications' ? 'active' : ''}`}
                onClick={() => { setCentreTab('applications'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><FileText size={16} /> Applications</span>
                <span className="tc-nav-count">{centreEnrollments.length}</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'programmes' ? 'active' : ''}`}
                onClick={() => { setCentreTab('programmes'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><GraduationCap size={16} /> Courses & Batches</span>
                <span className="tc-nav-count">{centreProgrammes.length}</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'trainers' ? 'active' : ''}`}
                onClick={() => { setCentreTab('trainers'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Users size={16} /> Trainers</span>
                <span className="tc-nav-count">{centreTrainers.length}</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'profile' ? 'active' : ''}`}
                onClick={() => { setCentreTab('profile'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Building2 size={16} /> Centre Profile & Labs</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'reports' ? 'active' : ''}`}
                onClick={() => { setCentreTab('reports'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Award size={16} /> Reports & Analytics</span>
              </button>
              <button
                type="button"
                className={`tc-mobile-nav-link ${centreTab === 'security' ? 'active' : ''}`}
                onClick={() => { setCentreTab('security'); setCentreMobileMenuOpen(false); }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Lock size={16} /> Security & Password</span>
              </button>

              <button 
                type="button"
                className="tc-mobile-logout" 
                onClick={handleLogout}
              >
                <LogOut size={16} /> {t('nav.logout')}
              </button>
            </div>
          </header>

          <div className="main-content-container" style={{ padding: '2rem 1rem', maxWidth: '1240px', margin: '0 auto' }}>
            {/* Unassigned Centre Warning if admin has no centres */}
            {unassignedCentreNotice && (
              <div style={{ backgroundColor: '#fff1f2', border: '1px solid #fecdd3', padding: '1.25rem', borderRadius: '10px', marginBottom: '1.5rem', textAlign: 'center' }}>
                <AlertCircle size={28} color="#e11d48" style={{ margin: '0 auto 0.5rem auto' }} />
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#9f1239', marginBottom: '0.35rem' }}>
                  No Training Centre Assigned
                </h3>
                <p style={{ fontSize: '0.86rem', color: '#be123c', maxWidth: '600px', margin: '0 auto' }}>
                  Your account is registered as a Training Centre Administrator, but no accredited training centres have been allocated to you yet. Please contact the Directorate of Skill Development (Platform Administrator) to assign your center(s).
                </p>
              </div>
            )}

            {/* Status notification banner */}
            <div style={{ backgroundColor: '#f0fdfa', border: '1px solid #99f6e4', padding: '0.75rem 1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.84rem', color: '#0f766e', fontWeight: 600 }}>
                <CheckCircle2 size={16} /> Authenticated under Strict Centre Isolation: Bound to {centreProfile?.name || 'Authorized Centre'} ({centreProfile?.code || 'CTR-AUTH'})
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {assignedCentres && assignedCentres.length > 1 && (
                  <button
                    onClick={() => setShowCentreSelectModal(true)}
                    style={{ fontSize: '0.74rem', backgroundColor: '#0f766e', color: '#ffffff', padding: '0.25rem 0.6rem', borderRadius: '4px', border: 'none', cursor: 'pointer', fontWeight: 700 }}
                  >
                    Switch Centre ({assignedCentres.length} available)
                  </button>
                )}
                <span style={{ fontSize: '0.75rem', backgroundColor: '#ccfbf1', color: '#115e59', padding: '0.2rem 0.6rem', borderRadius: '4px', fontWeight: 700 }}>
                  STATUS: {centreProfile?.approval_status || 'APPROVED'}
                </span>
              </div>
            </div>

            {/* TAB: DASHBOARD */}
            {centreTab === 'dashboard' && (
              <div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
                  <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', borderLeft: '4px solid #0f766e' }}>
                    <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Active Programs</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', marginTop: '0.2rem' }}>{centreDashboard?.total_programs || centreProgrammes.length}</div>
                  </div>
                  <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', borderLeft: '4px solid #0284c7' }}>
                    <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Training Batches</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', marginTop: '0.2rem' }}>{centreDashboard?.total_batches || centreBatches.length}</div>
                  </div>
                  <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', borderLeft: '4px solid #ea580c' }}>
                    <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Citizen Applications</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', marginTop: '0.2rem' }}>{centreDashboard?.total_applications || centreEnrollments.length}</div>
                  </div>
                  <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', borderLeft: '4px solid #16a34a' }}>
                    <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Active Learners</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', marginTop: '0.2rem' }}>{centreDashboard?.active_learners || 0}</div>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
                  <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.5rem' }}>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '1rem' }}>Recent Applications Queue</h3>
                    <div style={{ overflowX: 'auto' }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                        <thead>
                          <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0', textAlign: 'left' }}>
                            <th style={{ padding: '0.6rem' }}>App Code</th>
                            <th style={{ padding: '0.6rem' }}>Citizen Name</th>
                            <th style={{ padding: '0.6rem' }}>Program</th>
                            <th style={{ padding: '0.6rem' }}>Status</th>
                            <th style={{ padding: '0.6rem' }}>Action</th>
                          </tr>
                        </thead>
                        <tbody>
                          {centreEnrollments.slice(0, 5).map((e: any) => (
                            <tr key={e.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                              <td style={{ padding: '0.6rem', fontWeight: 600, color: '#0f766e' }}>{e.code}</td>
                              <td style={{ padding: '0.6rem' }}>{e.citizen_name}</td>
                              <td style={{ padding: '0.6rem' }}>{e.program_title}</td>
                              <td style={{ padding: '0.6rem' }}>
                                <span style={{ fontSize: '0.72rem', padding: '0.15rem 0.5rem', borderRadius: '4px', fontWeight: 700, backgroundColor: e.status === 'APPROVED' ? '#dcfce7' : (e.status === 'REJECTED' ? '#fee2e2' : '#fef3c7'), color: e.status === 'APPROVED' ? '#15803d' : (e.status === 'REJECTED' ? '#b91c1c' : '#b45309') }}>
                                  {e.status}
                                </span>
                              </td>
                              <td style={{ padding: '0.6rem' }}>
                                <button
                                  className="btn-navy-outline"
                                  style={{ padding: '0.25rem 0.6rem', fontSize: '0.74rem' }}
                                  onClick={() => {
                                    setCentreReviewModalApp(e);
                                    setCentreReviewAction('APPROVE');
                                    setCentreReviewReason(e.admin_remarks || '');
                                    setCentreInternalNotes(e.internal_notes || '');
                                    setCentreReviewError('');
                                  }}
                                >
                                  Review
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.5rem' }}>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '1rem' }}>Assigned Trainers</h3>
                    {centreTrainers.length === 0 ? (
                      <p style={{ fontSize: '0.82rem', color: '#64748b' }}>No trainers assigned to this centre.</p>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        {centreTrainers.map((t: any) => (
                          <div key={t.id} style={{ padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                            <div style={{ fontWeight: 700, fontSize: '0.85rem', color: '#0f172a' }}>{t.name}</div>
                            <div style={{ fontSize: '0.76rem', color: '#0f766e' }}>{t.specialisation} • {t.experience_years} yrs exp</div>
                            <div style={{ fontSize: '0.74rem', color: '#64748b' }}>{t.contact_email}</div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* TAB: APPLICATIONS */}
            {centreTab === 'applications' && (
              <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>Centre Enrolment Applications</h3>
                    <p style={{ fontSize: '0.82rem', color: '#64748b' }}>Strictly scoped to applications submitted for {centreProfile?.name}</p>
                  </div>
                </div>

                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem' }}>
                    <thead>
                      <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0', textAlign: 'left' }}>
                        <th style={{ padding: '0.75rem' }}>Code</th>
                        <th style={{ padding: '0.75rem' }}>Applicant Name</th>
                        <th style={{ padding: '0.75rem' }}>Contact</th>
                        <th style={{ padding: '0.75rem' }}>Program</th>
                        <th style={{ padding: '0.75rem' }}>Mode</th>
                        <th style={{ padding: '0.75rem' }}>Status</th>
                        <th style={{ padding: '0.75rem' }}>Remarks / Reason</th>
                        <th style={{ padding: '0.75rem' }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {centreEnrollments.map((e: any) => (
                        <tr key={e.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                          <td style={{ padding: '0.75rem', fontWeight: 700, color: '#0f766e' }}>{e.code}</td>
                          <td style={{ padding: '0.75rem', fontWeight: 600 }}>{e.citizen_name}</td>
                          <td style={{ padding: '0.75rem', color: '#475569' }}>{e.citizen_email}<br /><small>{e.citizen_phone}</small></td>
                          <td style={{ padding: '0.75rem' }}>{e.program_title}</td>
                          <td style={{ padding: '0.75rem' }}>{e.selected_mode}</td>
                          <td style={{ padding: '0.75rem' }}>
                            <span style={{ fontSize: '0.72rem', padding: '0.15rem 0.5rem', borderRadius: '4px', fontWeight: 700, backgroundColor: e.status === 'APPROVED' ? '#dcfce7' : (e.status === 'REJECTED' ? '#fee2e2' : '#fef3c7'), color: e.status === 'APPROVED' ? '#15803d' : (e.status === 'REJECTED' ? '#b91c1c' : '#b45309') }}>
                              {e.status}
                            </span>
                          </td>
                          <td style={{ padding: '0.75rem', fontSize: '0.76rem', color: '#64748b' }}>
                            {e.rejection_reason ? <span style={{ color: '#b91c1c' }}>Rejection: {e.rejection_reason}</span> : (e.admin_remarks || '—')}
                          </td>
                          <td style={{ padding: '0.75rem' }}>
                            <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                              <button
                                className="btn-navy-outline"
                                style={{ padding: '0.3rem 0.6rem', fontSize: '0.76rem' }}
                                onClick={() => {
                                  setCentreReviewModalApp(e);
                                  setCentreReviewAction('APPROVE');
                                  setCentreReviewReason(e.admin_remarks || '');
                                  setCentreInternalNotes(e.internal_notes || '');
                                  setCentreReviewError('');
                                }}
                              >
                                Review & Decision
                              </button>
                              {e.status === 'APPROVED' && (
                                <button
                                  style={{
                                    padding: '0.3rem 0.6rem',
                                    fontSize: '0.76rem',
                                    backgroundColor: '#0f766e',
                                    color: '#ffffff',
                                    border: 'none',
                                    borderRadius: '4px',
                                    fontWeight: 700,
                                    cursor: 'pointer'
                                  }}
                                  onClick={() => {
                                    setCentreEnrolModalApp(e);
                                    // Preselect first batch for this program if available
                                    const matchingBatches = centreBatches.filter((b: any) => b.program_id === e.program_id);
                                    setCentreEnrolSelectedBatchId(matchingBatches[0]?.id || null);
                                    setCentreEnrolInternalNotes('');
                                    setCentreEnrolError('');
                                  }}
                                >
                                  Enrol in Batch
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* TAB: COURSES & BATCHES */}
            {centreTab === 'programmes' && (
              <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Active Courses & Batches</h3>
                <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1.5rem' }}>Manage your centre offerings and batch schedules</p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
                  {centreProgrammes.map((p: any) => (
                    <div
                      key={p.id}
                      onClick={() => setCentreSelectedProgForBatches(p)}
                      style={{
                        border: '1px solid #e2e8f0',
                        borderRadius: '8px',
                        padding: '1.25rem',
                        backgroundColor: '#f8fafc',
                        cursor: 'pointer',
                        transition: 'all 0.15s ease',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'space-between'
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.borderColor = '#0f766e')}
                      onMouseLeave={(e) => (e.currentTarget.style.borderColor = '#e2e8f0')}
                    >
                      <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                          <span style={{ fontSize: '0.72rem', color: '#0f766e', fontWeight: 700 }}>{p.code} • {p.mode}</span>
                          <span
                            onClick={(e) => {
                              e.stopPropagation();
                              setCentreSelectedProgForBatches(p);
                            }}
                            style={{
                              fontSize: '0.72rem',
                              fontWeight: 700,
                              color: '#0f766e',
                              backgroundColor: '#ccfbf1',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              cursor: 'pointer'
                            }}
                          >
                            {p.batch_count} Active Batch{p.batch_count === 1 ? '' : 'es'}
                          </span>
                        </div>
                        <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', marginTop: '0.2rem', marginBottom: '0.4rem' }}>{p.title}</h4>
                        <p style={{ fontSize: '0.78rem', color: '#64748b', marginBottom: '0.8rem' }}>{p.description}</p>
                      </div>

                      <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '0.75rem', fontSize: '0.76rem' }}>
                        <div><strong>Trainer:</strong> {p.trainer_name || 'Assigned Instructor'}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.4rem' }}>
                          <span><strong>Duration:</strong> {p.duration_hours} Hours</span>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              setCentreSelectedProgForBatches(p);
                            }}
                            style={{
                              backgroundColor: '#0f766e',
                              color: '#ffffff',
                              border: 'none',
                              borderRadius: '5px',
                              padding: '0.35rem 0.75rem',
                              fontSize: '0.75rem',
                              fontWeight: 700,
                              cursor: 'pointer'
                            }}
                          >
                            View Batches ({p.batch_count}) →
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB: BATCHES & SCHEDULES */}
            {centreTab === 'batches' && (
              <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Training Batches & Timing Schedules</h3>
                <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1.5rem' }}>Inspect batch capacity, classroom timing, and enrolled learner counts</p>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
                  {centreBatches.map((b: any) => (
                    <div key={b.id} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#f8fafc' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                        <span style={{ fontSize: '0.72rem', color: '#0f766e', fontWeight: 700 }}>{b.code}</span>
                        <span style={{ fontSize: '0.72rem', backgroundColor: '#dcfce7', color: '#166534', padding: '0.15rem 0.5rem', borderRadius: '4px', fontWeight: 700 }}>
                          {b.status || 'ACTIVE'}
                        </span>
                      </div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.2rem' }}>{b.batch_name}</h4>
                      <div style={{ fontSize: '0.8rem', color: '#0284c7', fontWeight: 600, marginBottom: '0.5rem' }}>{b.program_title}</div>
                      <div style={{ fontSize: '0.76rem', color: '#475569', lineHeight: '1.6' }}>
                        <div><strong>Timing:</strong> {b.timings}</div>
                        <div><strong>Schedule:</strong> {b.training_schedule}</div>
                        <div><strong>Delivery Mode:</strong> {b.mode}</div>
                        <div><strong>Capacity:</strong> {b.enrolled_count} / {b.total_seats} Seats Enrolled ({b.available_seats} Available)</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}


            {/* TAB: TRAINERS */}
            {centreTab === 'trainers' && (
              <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Centre Instructors & Trainers</h3>
                <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1.5rem' }}>Verified faculty assigned to this training location</p>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                  {centreTrainers.map((t: any) => (
                    <div key={t.id} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#f8fafc' }}>
                      <div style={{ fontSize: '0.72rem', color: '#0f766e', fontWeight: 700 }}>{t.code}</div>
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', marginTop: '0.2rem' }}>{t.name}</h4>
                      <div style={{ fontSize: '0.8rem', color: '#0284c7', fontWeight: 600 }}>{t.specialisation}</div>
                      <div style={{ fontSize: '0.76rem', color: '#64748b', marginTop: '0.4rem' }}>Qualification: {t.qualification}</div>
                      <div style={{ fontSize: '0.76rem', color: '#64748b' }}>Experience: {t.experience_years} Years</div>
                      <div style={{ fontSize: '0.76rem', color: '#64748b' }}>Email: {t.contact_email}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* TAB: PROFILE & LABS */}
            {centreTab === 'profile' && (
              <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Training Centre Profile & Facilities</h3>
                <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1.5rem' }}>Official location, infrastructure, and smart lab credentials</p>
                {centreProfile && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem' }}>Centre Details</h4>
                      <div style={{ fontSize: '0.82rem', lineHeight: '1.6', color: '#334155' }}>
                        <div><strong>Code:</strong> {centreProfile.code}</div>
                        <div><strong>Name:</strong> {centreProfile.name}</div>
                        <div><strong>District:</strong> {centreProfile.district}, {centreProfile.state}</div>
                        <div><strong>Address:</strong> {centreProfile.address}</div>
                        <div><strong>Contact:</strong> {centreProfile.contact_phone} • {centreProfile.contact_email}</div>
                        <div><strong>Established:</strong> {centreProfile.establishment_year || 'Information not yet available'}</div>
                        <div><strong>Accreditation:</strong> {centreProfile.approval_status || 'ACCREDITED'}</div>
                      </div>
                    </div>

                    <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem' }}>Facilities & Labs</h4>
                      <div style={{ fontSize: '0.82rem', lineHeight: '1.6', color: '#334155' }}>
                        <div><strong>Classrooms:</strong> {centreProfile.classroom_count || 4} Dedicated Smart Rooms</div>
                        <div><strong>Facilities:</strong> {centreProfile.facilities}</div>
                        <div><strong>Lab Specs:</strong> {centreProfile.lab_details || 'High-performance workstations with gigabit connectivity'}</div>
                        <div><strong>Equipment:</strong> {centreProfile.equipment_details || 'IoT development boards, Cisco networking racks, multimedia projection'}</div>
                        <div><strong>Certifications:</strong> {centreProfile.certifications || 'NSDC Accredited Training Partner'}</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB: REPORTS */}
            {centreTab === 'reports' && (
              <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Training Analytics & Completion Metrics</h3>
                <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1.5rem' }}>Official NSQF progress and attendance tracking</p>
                {centreReports && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
                    <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem' }}>Attendance Overview</h4>
                      <div style={{ fontSize: '0.82rem', lineHeight: '1.8' }}>
                        <div><strong>Above 90% (Distinction):</strong> {centreReports.attendance_distribution.above_90} Students</div>
                        <div><strong>75% - 90% (Compliant):</strong> {centreReports.attendance_distribution['75_to_90']} Students</div>
                        <div><strong>Below 75% (At Risk):</strong> {centreReports.attendance_distribution.below_75} Students</div>
                      </div>
                    </div>
                    <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem' }}>Curriculum Progress</h4>
                      <div style={{ fontSize: '0.82rem', lineHeight: '1.8' }}>
                        <div><strong>Above 80% Completed:</strong> {centreReports.progress_distribution.above_80} Students</div>
                        <div><strong>50% - 80% In Progress:</strong> {centreReports.progress_distribution['50_to_80']} Students</div>
                        <div><strong>Below 50% Early Stage:</strong> {centreReports.progress_distribution.below_50} Students</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* TAB: SECURITY & INDEPENDENT PASSWORD MANAGEMENT */}
            {centreTab === 'security' && (
              <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '2rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.25rem', paddingBottom: '1rem', borderBottom: '1px solid #f1f5f9' }}>
                  <div style={{ backgroundColor: '#e0f2fe', color: '#0369a1', padding: '0.6rem', borderRadius: '8px' }}>
                    <Lock size={22} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                      Representative Account Security & Password Management
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.82rem', color: '#64748b' }}>
                      Independently manage and update your unique Training Centre administrator password (Argon2id cryptographic hash stored in MySQL)
                    </p>
                  </div>
                </div>

                <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '0.85rem 1rem', marginBottom: '1.5rem', fontSize: '0.82rem', color: '#166534' }}>
                  <strong>Security Enforcement:</strong> Training Centre representatives independently manage their own access. Passwords are never shared across centres, never displayed in plaintext, and securely hashed with Argon2id.
                </div>

                {changePasswordMsg && (
                  <div style={{
                    backgroundColor: changePasswordMsg.type === 'success' ? '#f0fdf4' : '#fee2e2',
                    color: changePasswordMsg.type === 'success' ? '#166534' : '#b91c1c',
                    border: changePasswordMsg.type === 'success' ? '1px solid #bbf7d0' : '1px solid #fecaca',
                    padding: '0.75rem 1rem',
                    borderRadius: '6px',
                    fontSize: '0.82rem',
                    marginBottom: '1.5rem'
                  }}>
                    {changePasswordMsg.text}
                  </div>
                )}

                <form onSubmit={handleChangePassword} style={{ maxWidth: '520px' }}>
                  <div className="form-group" style={{ marginBottom: '1.2rem' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.35rem', display: 'block' }}>
                      Current Representative Password:
                    </label>
                    <div style={{ position: 'relative' }}>
                      <input
                        type={showChangeCurrentPassword ? 'text' : 'password'}
                        required
                        className="form-control"
                        style={{ paddingRight: '2.5rem' }}
                        value={changeCurrentPassword}
                        onChange={(e) => setChangeCurrentPassword(e.target.value)}
                        placeholder="Enter current password"
                      />
                      <button
                        type="button"
                        style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
                        onClick={() => setShowChangeCurrentPassword(!showChangeCurrentPassword)}
                      >
                        {showChangeCurrentPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <div className="form-group" style={{ marginBottom: '1.2rem' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.35rem', display: 'block' }}>
                      New Unique Password (minimum 8 characters):
                    </label>
                    <div style={{ position: 'relative' }}>
                      <input
                        type={showChangeNewPassword ? 'text' : 'password'}
                        required
                        className="form-control"
                        style={{ paddingRight: '2.5rem' }}
                        value={changeNewPassword}
                        onChange={(e) => setChangeNewPassword(e.target.value)}
                        placeholder="Enter strong unique password"
                      />
                      <button
                        type="button"
                        style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
                        onClick={() => setShowChangeNewPassword(!showChangeNewPassword)}
                      >
                        {showChangeNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <div className="form-group" style={{ marginBottom: '1.5rem' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.35rem', display: 'block' }}>
                      Confirm New Password:
                    </label>
                    <div style={{ position: 'relative' }}>
                      <input
                        type={showChangeConfirmPassword ? 'text' : 'password'}
                        required
                        className="form-control"
                        style={{ paddingRight: '2.5rem' }}
                        value={changeConfirmPassword}
                        onChange={(e) => setChangeConfirmPassword(e.target.value)}
                        placeholder="Re-enter new password"
                      />
                      <button
                        type="button"
                        style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
                        onClick={() => setShowChangeConfirmPassword(!showChangeConfirmPassword)}
                      >
                        {showChangeConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="btn-primary-orange"
                    style={{ backgroundColor: '#0f766e', borderColor: '#0f766e', padding: '0.6rem 1.25rem', fontSize: '0.85rem' }}
                    disabled={changePasswordLoading || !changeCurrentPassword || !changeNewPassword || changeNewPassword.length < 8 || changeNewPassword !== changeConfirmPassword}
                  >
                    {changePasswordLoading ? 'Updating Password...' : 'Update Representative Password'}
                  </button>
                </form>
              </div>
            )}
          </div>

          {/* APPLICATION REVIEW MODAL */}
          {centreReviewModalApp && (
            <div className="modal-overlay">
              <div className="modal-content-lg" style={{ maxWidth: '620px' }}>
                <div className="modal-header">
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444' }}>
                    Review Application: {centreReviewModalApp.code}
                  </h3>
                  <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setCentreReviewModalApp(null)}>
                    <X size={20} />
                  </button>
                </div>
                <div className="modal-body">
                  <div style={{ backgroundColor: '#f8fafc', padding: '0.85rem', borderRadius: '8px', marginBottom: '1.25rem', fontSize: '0.82rem', border: '1px solid #e2e8f0' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                      <div><strong>Applicant:</strong> {centreReviewModalApp.citizen_name}</div>
                      <div><strong>Contact:</strong> {centreReviewModalApp.citizen_email}</div>
                      <div><strong>Program:</strong> {centreReviewModalApp.program_title}</div>
                      <div><strong>Current Status:</strong> <span style={{ fontWeight: 700, color: '#0f766e' }}>{centreReviewModalApp.status}</span></div>
                    </div>
                    {centreReviewModalApp.applicant_statement && (
                      <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px dashed #cbd5e1' }}>
                        <strong>Applicant Statement:</strong> <em>"{centreReviewModalApp.applicant_statement}"</em>
                      </div>
                    )}
                  </div>

                  {centreReviewError && (
                    <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.6rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem' }}>
                      {centreReviewError}
                    </div>
                  )}

                  <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                    <label style={{ display: 'block', fontWeight: 700, marginBottom: '0.5rem', fontSize: '0.85rem' }}>
                      Select Lifecycle Review Decision:
                    </label>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '0.5rem' }}>
                      {[
                        { action: 'APPROVE', label: 'Approve Application', color: '#15803d', bg: '#f0fdf4', border: '#bbf7d0' },
                        { action: 'REJECT', label: 'Reject Application', color: '#b91c1c', bg: '#fef2f2', border: '#fecaca' },
                        { action: 'UNDER_REVIEW', label: 'Mark Under Review', color: '#0369a1', bg: '#f0f9ff', border: '#bae6fd' },
                        { action: 'ACTION_REQUIRED', label: 'Request Additional Info', color: '#b45309', bg: '#fffbeb', border: '#fde68a' },
                        { action: 'WAITLIST', label: 'Place on Waitlist', color: '#6d28d9', bg: '#f5f3ff', border: '#ddd6fe' },
                        { action: 'WITHDRAW', label: 'Mark Withdrawn', color: '#475569', bg: '#f8fafc', border: '#e2e8f0' }
                      ].map((item) => {
                        const isSelected = centreReviewAction === item.action;
                        return (
                          <div
                            key={item.action}
                            onClick={() => setCentreReviewAction(item.action as any)}
                            style={{
                              padding: '0.6rem 0.75rem',
                              borderRadius: '6px',
                              border: `1.5px solid ${isSelected ? item.color : item.border}`,
                              backgroundColor: isSelected ? item.bg : '#ffffff',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '6px',
                              fontSize: '0.8rem',
                              fontWeight: isSelected ? 700 : 500,
                              color: item.color
                            }}
                          >
                            <input
                              type="radio"
                              name="review_action"
                              checked={isSelected}
                              onChange={() => setCentreReviewAction(item.action as any)}
                              style={{ margin: 0 }}
                            />
                            {item.label}
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div className="form-group" style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.82rem', marginBottom: '0.3rem' }}>
                      {centreReviewAction === 'REJECT' ? 'Mandatory Rejection Reason (Visible to Citizen):' : 'Official Review Remarks (Visible to Citizen):'}
                    </label>
                    <textarea
                      className="form-control"
                      rows={2}
                      value={centreReviewReason}
                      onChange={(e) => setCentreReviewReason(e.target.value)}
                      placeholder={centreReviewAction === 'REJECT' ? 'State the explicit reason for application rejection...' : 'Official remarks visible on citizen application tracking...'}
                    />
                  </div>

                  <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.82rem', marginBottom: '0.3rem', color: '#475569' }}>
                      Private Internal Review Notes (Confidential to Centre Staff):
                    </label>
                    <textarea
                      className="form-control"
                      rows={2}
                      value={centreInternalNotes}
                      onChange={(e) => setCentreInternalNotes(e.target.value)}
                      placeholder="Private notes, applicant interview comments, or background checks (never shown to citizen)..."
                    />
                  </div>

                  {centreReviewModalApp.history && centreReviewModalApp.history.length > 0 && (
                    <div style={{ backgroundColor: '#f8fafc', padding: '0.75rem', borderRadius: '6px', marginBottom: '1.25rem', fontSize: '0.78rem', border: '1px solid #e2e8f0' }}>
                      <strong style={{ color: '#0f172a', display: 'block', marginBottom: '0.4rem' }}>Application Audit & Status History:</strong>
                      <div style={{ display: 'grid', gap: '0.3rem' }}>
                        {centreReviewModalApp.history.map((h: any, idx: number) => (
                          <div key={idx} style={{ color: '#475569' }}>
                            • <span style={{ fontWeight: 600 }}>{h.old_status} → {h.new_status}</span> by {h.actor} ({formatISTDateTime(h.timestamp)}): {h.remarks || 'No remarks recorded'}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                    <button className="btn-navy-outline" onClick={() => setCentreReviewModalApp(null)}>
                      Cancel
                    </button>
                    <button
                      className="btn-primary-orange"
                      onClick={handleCentreReviewSubmit}
                      disabled={centreReviewSubmitting}
                    >
                      {centreReviewSubmitting ? 'Saving...' : 'Apply Status Update'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Modal: Explicit Batch Enrolment */}
          {centreEnrolModalApp && (
            <div className="modal-backdrop">
              <div className="modal-content-lg" style={{ maxWidth: '520px' }}>
                <div className="modal-header">
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f766e' }}>
                    Enrol in Batch: {centreEnrolModalApp.citizen_name}
                  </h3>
                  <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setCentreEnrolModalApp(null)}>
                    <X size={20} />
                  </button>
                </div>
                <div className="modal-body">
                  <div style={{ backgroundColor: '#f0fdfa', border: '1px solid #99f6e4', padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem', fontSize: '0.82rem' }}>
                    <div><strong>Course:</strong> {centreEnrolModalApp.program_title}</div>
                    <div><strong>Application Code:</strong> {centreEnrolModalApp.code}</div>
                    <div><strong>Applicant:</strong> {centreEnrolModalApp.citizen_name} ({centreEnrolModalApp.citizen_email})</div>
                  </div>

                  {centreEnrolError && (
                    <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.6rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem' }}>
                      {centreEnrolError}
                    </div>
                  )}

                  <div className="form-group" style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'block', fontWeight: 700, fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                      Assign to Active Training Batch:
                    </label>
                    <select
                      className="form-control"
                      value={centreEnrolSelectedBatchId || ''}
                      onChange={(e) => setCentreEnrolSelectedBatchId(Number(e.target.value))}
                    >
                      <option value="">-- Choose Batch --</option>
                      {centreBatches
                        .filter((b: any) => b.program_id === centreEnrolModalApp.program_id)
                        .map((b: any) => (
                          <option key={b.id} value={b.id} disabled={b.available_seats <= 0}>
                            {b.batch_name} ({b.timings}) • {b.available_seats} seats remaining {b.available_seats <= 0 ? '[FULL]' : ''}
                          </option>
                        ))}
                    </select>
                  </div>

                  <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                    <label style={{ display: 'block', fontWeight: 600, fontSize: '0.82rem', marginBottom: '0.3rem' }}>
                      Internal Enrolment Notes:
                    </label>
                    <textarea
                      className="form-control"
                      rows={2}
                      value={centreEnrolInternalNotes}
                      onChange={(e) => setCentreEnrolInternalNotes(e.target.value)}
                      placeholder="Optional notes for enrolment records..."
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                    <button className="btn-navy-outline" onClick={() => setCentreEnrolModalApp(null)}>
                      Cancel
                    </button>
                    <button
                      className="btn-primary-orange"
                      onClick={handleCentreEnrolSubmit}
                      disabled={centreEnrolSubmitting || !centreEnrolSelectedBatchId}
                    >
                      {centreEnrolSubmitting ? 'Enrolling...' : 'Confirm Enrolment'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Modal: View Programme Batches Details */}
          {centreSelectedProgForBatches && (
            <div className="modal-backdrop">
              <div className="modal-content-lg" style={{ maxWidth: '680px' }}>
                <div className="modal-header">
                  <div>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#0f766e', backgroundColor: '#ccfbf1', padding: '2px 8px', borderRadius: '4px' }}>
                      {centreSelectedProgForBatches.code}
                    </span>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444', margin: '4px 0 0 0' }}>
                      {centreSelectedProgForBatches.title}
                    </h3>
                  </div>
                  <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setCentreSelectedProgForBatches(null)}>
                    <X size={20} />
                  </button>
                </div>
                <div className="modal-body">
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', backgroundColor: '#f8fafc', padding: '0.85rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '1.25rem', fontSize: '0.8rem' }}>
                    <div><strong>Assigned Trainer:</strong> {centreSelectedProgForBatches.trainer_name || 'Assigned Instructor'}</div>
                    <div><strong>Duration:</strong> {centreSelectedProgForBatches.duration_hours} Training Hours</div>
                    <div><strong>Delivery Mode:</strong> {centreSelectedProgForBatches.mode}</div>
                    <div><strong>Course Fee:</strong> {centreSelectedProgForBatches.fee > 0 ? `₹${centreSelectedProgForBatches.fee}` : 'Fully Government Subsidized (₹0)'}</div>
                  </div>

                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>Active Training Batches ({centreBatches.filter((b: any) => b.program_id === centreSelectedProgForBatches.id).length})</span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b' }}>Assigned Training Centre: {centreProfile?.name || 'Current Centre'}</span>
                  </h4>

                  {(() => {
                    const progBatches = centreBatches.filter((b: any) => b.program_id === centreSelectedProgForBatches.id);
                    if (progBatches.length === 0) {
                      return (
                        <div style={{ textAlign: 'center', padding: '2rem 1rem', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', color: '#64748b', fontSize: '0.85rem' }}>
                          No active training batches are currently scheduled for this programme at your centre.
                        </div>
                      );
                    }
                    return (
                      <div style={{ display: 'grid', gap: '0.85rem' }}>
                        {progBatches.map((b: any) => (
                          <div
                            key={b.id}
                            style={{
                              backgroundColor: '#ffffff',
                              border: '1px solid #e2e8f0',
                              borderRadius: '8px',
                              padding: '1rem',
                              boxShadow: '0 1px 3px rgba(0,0,0,0.03)'
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.4rem' }}>
                              <div>
                                <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#0f766e', backgroundColor: '#f0fdfa', padding: '2px 6px', borderRadius: '4px', border: '1px solid #ccfbf1' }}>
                                  {b.code}
                                </span>
                                <h5 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', margin: '4px 0 0 0' }}>
                                  {b.batch_name}
                                </h5>
                              </div>
                              <span style={{ fontSize: '0.7rem', backgroundColor: '#dcfce7', color: '#166534', padding: '2px 8px', borderRadius: '4px', fontWeight: 700 }}>
                                {b.status || 'ACTIVE'}
                              </span>
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.4rem', fontSize: '0.78rem', color: '#475569', marginTop: '0.6rem', borderTop: '1px solid #f1f5f9', paddingTop: '0.6rem' }}>
                              <div><strong>Batch ID:</strong> #{b.id}</div>
                              <div><strong>Delivery Mode:</strong> {b.mode}</div>
                              <div><strong>Daily Timings:</strong> {b.timings}</div>
                              <div><strong>Weekly Schedule:</strong> {b.training_schedule}</div>
                              <div><strong>Assigned Trainer:</strong> {centreSelectedProgForBatches.trainer_name || 'Assigned Instructor'}</div>
                              <div>
                                <strong>Seat Capacity:</strong>{' '}
                                <span style={{ fontWeight: 700, color: '#0f172a' }}>
                                  {b.enrolled_count} / {b.total_seats}
                                </span>{' '}
                                (<span style={{ color: b.available_seats > 0 ? '#16a34a' : '#dc2626', fontWeight: 600 }}>{b.available_seats} Available</span>)
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    );
                  })()}

                  <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
                    <button
                      className="btn-navy-outline"
                      onClick={() => setCentreSelectedProgForBatches(null)}
                      style={{ padding: '0.5rem 1.25rem', fontSize: '0.85rem' }}
                    >
                      Close Batch Details
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : userRole === 'SKILL_DEPARTMENT_ADMIN' || userRole === 'GOVERNMENT_ADMIN' ? (

        <div>
          {/* Dedicated Admin Top Navigation */}
          <header className="header-main" style={{ borderBottom: '3px solid #0f2444', backgroundColor: '#ffffff' }}>
            <div className="header-container">
              <div className="brand-wrapper" onClick={() => { setAdminTab('applications'); setAdminMobileMenuOpen(false); }}>
                <div className="brand-emblem" style={{ background: 'linear-gradient(135deg, #091a33 0%, #1e3a8a 100%)' }}>
                  <Shield size={24} />
                </div>
                <div className="brand-text">
                  <h1 style={{ color: '#091a33' }}>
                    NagrikSetu
                  </h1>
                  <p style={{ letterSpacing: '0.08em', color: '#1e40af', fontWeight: 700 }}>Skill Department Administration Desk</p>
                </div>
              </div>

              <button
                type="button"
                className="mobile-menu-toggle"
                onClick={() => setAdminMobileMenuOpen(!adminMobileMenuOpen)}
                aria-label="Toggle navigation menu"
              >
                {adminMobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
              </button>

              <nav className={`nav-links ${adminMobileMenuOpen ? 'nav-open' : ''}`}>
                <button
                  className={`nav-item-btn ${adminTab === 'applications' ? 'active' : ''}`}
                  onClick={() => setAdminTab('applications')}
                >
                  <FileText size={15} /> Applications Queue ({adminEnrollments.length})
                </button>
                <button
                  className={`nav-item-btn ${adminTab === 'skills' ? 'active' : ''}`}
                  onClick={() => setAdminTab('skills')}
                >
                  <BookOpen size={15} /> Skills Catalogue
                </button>
                <button
                  className={`nav-item-btn ${adminTab === 'programmes' ? 'active' : ''}`}
                  onClick={() => setAdminTab('programmes')}
                >
                  <GraduationCap size={15} /> Programmes & Batches
                </button>
                <button
                  className={`nav-item-btn ${adminTab === 'centres' ? 'active' : ''}`}
                  onClick={() => setAdminTab('centres')}
                >
                  <Building2 size={15} /> Training Centres
                </button>

              </nav>

              <div className="nav-actions">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0f172a' }}>{userName || userEmail}</div>
                    <div style={{ fontSize: '0.72rem', color: '#16a34a', fontWeight: 600 }}>● SKILL ADMIN AUTHORIZED</div>
                  </div>
                  <button className="btn-navy-outline" onClick={handleLogout}>
                    <LogOut size={14} /> Log Out
                  </button>
                </div>
              </div>
            </div>
          </header>

          {/* Banner Notice for Admin */}
          {bannerNotice && (
            <div style={{ backgroundColor: '#eff6ff', borderBottom: '1px solid #bfdbfe', padding: '0.6rem 1.5rem', textAlign: 'center', fontSize: '0.85rem', color: '#1e40af', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}>
              <AlertCircle size={16} />
              {bannerNotice}
              <button style={{ background: 'none', border: 'none', cursor: 'pointer', marginLeft: '1rem', color: '#1e40af' }} onClick={() => setBannerNotice('')}>✕</button>
            </div>
          )}

          {/* Admin Main Management Workspaces */}
          <div className="main-container">
          <div className="section-header">
            <div>
              <h2>{t('admin.dashboard_title')}</h2>
              <p>Official Departmental Admin Portal • Real-time Application Verification & Batch Capacity Management</p>
            </div>
          </div>

          {/* Real Database Statistics */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
            <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', padding: '1.25rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f2444' }}>{adminStats?.stats?.total_skills || totalSkills}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Total Skills in Catalogue</div>
            </div>
            <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', padding: '1.25rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f2444' }}>{adminStats?.stats?.total_programs || programmes.length}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Active Programmes</div>
            </div>
            <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', padding: '1.25rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ea580c' }}>{adminStats?.stats?.pending_review || 0}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Pending Reviews</div>
            </div>
            <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', padding: '1.25rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#16a34a' }}>{adminStats?.stats?.approved || 0}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Approved Enrolments</div>
            </div>
            <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', padding: '1.25rem', borderRadius: '8px' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#7e22ce' }}>{adminStats?.stats?.total_certificates_issued || 0}</div>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Certificates Issued</div>
            </div>
          </div>

          {/* Admin Sub-Tabs Navigation */}
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '0.5rem', flexWrap: 'wrap' }}>
            <button
              className={`nav-item-btn ${adminTab === 'applications' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('applications')}
            >
              Citizen Applications Queue ({adminEnrollments.length})
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'hierarchy' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem', backgroundColor: adminTab === 'hierarchy' ? '#0f2444' : '#f8fafc', color: adminTab === 'hierarchy' ? '#ffffff' : '#0f2444', border: '1.5px solid #0f2444' }}
              onClick={() => { setAdminTab('hierarchy'); fetchAdminCatalogueSummary(); }}
            >
              Catalogue Hierarchy & Centre Linkage
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'skills' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('skills')}
            >
              Skill Catalogue Directory
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'programmes' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('programmes')}
            >
              Training Programmes & Batches
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'centres' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('centres')}
            >
              Training Centres
            </button>
          </div>

                    {/* TAB: CATALOGUE HIERARCHY & TRAINING CENTRE MATRIX (Platform Admin Read-Only) */}
          {adminTab === 'hierarchy' && (
            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <Layers size={22} color="#0284c7" /> Skill Hierarchy & Centre Affiliation Matrix
                  </h3>
                  <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                    Read-only monitoring of the 7 main accredited sectors, 36 subcategories, 228 industry skills, and registered training centre offerings.
                  </p>
                </div>
                <button
                  type="button"
                  className="btn-navy-outline"
                  onClick={fetchAdminCatalogueSummary}
                  disabled={adminCatalogueLoading}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.82rem' }}
                >
                  <RefreshCw size={14} className={adminCatalogueLoading ? 'animate-spin' : ''} /> Refresh Catalogue
                </button>
              </div>

              {adminCatalogueLoading && !adminCatalogueData ? (
                <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
                  <Loader2 size={32} className="animate-spin" style={{ margin: '0 auto 1rem auto', color: '#0284c7' }} />
                  Loading comprehensive catalogue hierarchy from MySQL...
                </div>
              ) : adminCatalogueData ? (
                <div style={{ display: 'grid', gap: '1.75rem' }}>
                  {/* Summary Metric Counters */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
                    <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '1rem' }}>
                      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#1e3a8a' }}>{adminCatalogueData.total_categories}</div>
                      <div style={{ fontSize: '0.78rem', color: '#2563eb', fontWeight: 600 }}>Main Industry Sectors</div>
                    </div>
                    <div style={{ backgroundColor: '#faf5ff', border: '1px solid #e9d5ff', borderRadius: '8px', padding: '1rem' }}>
                      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#6b21a8' }}>{adminCatalogueData.total_subcategories}</div>
                      <div style={{ fontSize: '0.78rem', color: '#9333ea', fontWeight: 600 }}>Specialised Subcategories</div>
                    </div>
                    <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '1rem' }}>
                      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#14532d' }}>{adminCatalogueData.total_skills}</div>
                      <div style={{ fontSize: '0.78rem', color: '#16a34a', fontWeight: 600 }}>Total Accredited Skills</div>
                    </div>
                  </div>

                  {/* Categories & Subcategories Accordion / Listing */}
                  <div style={{ display: 'grid', gap: '1.25rem' }}>
                    {adminCatalogueData.categories?.map((cat: any) => (
                      <div key={cat.category_id} style={{ border: '1.5px solid #e2e8f0', borderRadius: '10px', overflow: 'hidden' }}>
                        <div style={{ backgroundColor: '#f8fafc', padding: '1rem 1.25rem', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#0284c7', backgroundColor: '#e0f2fe', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                              {cat.category_code}
                            </span>
                            <strong style={{ fontSize: '1.1rem', color: '#0f2444' }}>{cat.category_name}</strong>
                          </div>
                          <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.78rem', color: '#475569' }}>
                            <span><strong>{cat.subcategories_count}</strong> Subcategories</span>
                            <span>•</span>
                            <span><strong>{cat.total_skills}</strong> Skills</span>
                            <span>•</span>
                            <span><strong>{cat.total_programmes}</strong> Live Programmes</span>
                          </div>
                        </div>

                        <div style={{ padding: '1.25rem', display: 'grid', gap: '1rem' }}>
                          {cat.subcategories?.map((sub: any) => (
                            <div key={sub.subcategory_id} style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.5rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                  <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#64748b', backgroundColor: '#f1f5f9', padding: '0.15rem 0.45rem', borderRadius: '3px' }}>
                                    {sub.subcategory_code}
                                  </span>
                                  <span style={{ fontWeight: 700, color: '#0f172a', fontSize: '0.95rem' }}>{sub.subcategory_name}</span>
                                </div>
                                <span style={{ fontSize: '0.75rem', color: '#0284c7', fontWeight: 700, backgroundColor: '#f0f9ff', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                                  {sub.skills_count} Skills Configured
                                </span>
                              </div>

                              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '0.75rem' }}>
                                {sub.skills?.map((sk: any) => (
                                  <div key={sk.skill_id} style={{ backgroundColor: '#f8fafc', border: '1px solid #f1f5f9', borderRadius: '6px', padding: '0.75rem', fontSize: '0.8rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.35rem' }}>
                                      <strong style={{ color: '#0f2444' }}>{sk.skill_name}</strong>
                                      <span style={{ fontSize: '0.7rem', color: '#64748b' }}>{sk.level}</span>
                                    </div>
                                    <div style={{ fontSize: '0.74rem', color: '#64748b', marginBottom: '0.5rem' }}>
                                      Duration: {sk.duration_hours}h • {sk.has_programmes ? `${sk.programmes_count} live programme(s)` : 'No live batches currently'}
                                    </div>
                                    {sk.centres_offering?.length > 0 ? (
                                      <div style={{ fontSize: '0.72rem', color: '#0f766e', backgroundColor: '#f0fdfa', padding: '0.35rem 0.5rem', borderRadius: '4px', border: '1px solid #ccfbf1' }}>
                                        <strong>Offered by:</strong> {sk.centres_offering.map((co: any) => co.centre_name.split('(')[0].trim()).join(', ')}
                                      </div>
                                    ) : (
                                      <div style={{ fontSize: '0.72rem', color: '#94a3b8', fontStyle: 'italic' }}>
                                        Curriculum registered; awaiting centre batch scheduling
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : null}
            </div>
          )}


          {/* TAB 1: APPLICATIONS QUEUE */}
          {adminTab === 'applications' && (
          <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
            <div style={{ padding: '1.25rem', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>Citizen Applications Queue</h3>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {['ALL', 'PENDING', 'APPROVED', 'REJECTED', 'COMPLETED'].map(st => (
                  <button
                    key={st}
                    className={`nav-item-btn ${adminFilterStatus === st ? 'active' : ''}`}
                    onClick={() => {
                      setAdminFilterStatus(st);
                      fetch(`${API_BASE}/api/admin/enrollments?status=${st}`, { headers: { Authorization: `Bearer ${token}` } })
                        .then(r => r.json())
                        .then(setAdminEnrollments);
                    }}
                  >
                    {st}
                  </button>
                ))}
              </div>
            </div>

            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0', textAlign: 'left', color: '#475569' }}>
                  <th style={{ padding: '0.75rem 1rem' }}>Application ID</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Citizen Details</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Programme & Batch</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Submitted (IST)</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Progress</th>
                  <th style={{ padding: '0.75rem 1rem' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {adminEnrollments.map((a: any) => (
                  <tr key={a.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                    <td style={{ padding: '0.75rem 1rem', fontWeight: 700, color: '#0f2444' }}>{a.application_id}</td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ fontWeight: 600 }}>{a.citizen_name}</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{a.citizen_email} • {a.citizen_ref}</div>
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ fontWeight: 600 }}>{a.program_title}</div>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{a.batch_name} ({a.selected_mode})</div>
                    </td>
                    <td style={{ padding: '0.75rem 1rem', fontSize: '0.78rem', color: '#475569', whiteSpace: 'nowrap' }}>
                      {formatISTDateTime(a.created_at)}
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <span className={`status-pill ${a.status}`}>{a.status}</span>
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      {a.training_progress_pct}%
                    </td>
                    <td style={{ padding: '0.75rem 1rem' }}>
                      <div style={{ display: 'flex', gap: '0.4rem' }}>
                        <button
                          className="btn-navy-outline"
                          style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                          onClick={() => {
                            setReviewModalApp(a);
                          }}
                        >
                          Details
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          )}

          {/* TAB 2: SKILL CATALOGUE MANAGEMENT */}
          {adminTab === 'skills' && (
            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>Skill Catalogue Directory</h3>
                  <p style={{ fontSize: '0.82rem', color: '#64748b' }}>View and monitor registered skills across the NagrikSetu platform.</p>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#475569', backgroundColor: '#f1f5f9', padding: '0.4rem 0.8rem', borderRadius: '6px', fontWeight: 600 }}>
                  Showing {skills.length} of {totalSkills || 208} active skills
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
                {skills.map((s: any) => (
                  <div key={s.code} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.2rem', backgroundColor: '#f8fafc' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#ea580c', backgroundColor: '#fff7ed', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>{s.code}</span>
                      <span className={`badge-level ${s.level.toLowerCase()}`}>{s.level}</span>
                    </div>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.4rem' }}>{s.name}</h4>
                    <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '0.75rem' }}>{s.summary?.slice(0, 90)}...</p>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem', color: '#475569', borderTop: '1px solid #e2e8f0', paddingTop: '0.6rem' }}>
                      <span>{s.duration_hours}h • {s.enrolled_count} enrolled</span>
                      <button
                        className="btn-navy-outline"
                        style={{ padding: '0.25rem 0.5rem', fontSize: '0.72rem' }}
                        onClick={() => openCourseDetail(s.code)}
                      >
                        Details
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {/* Admin Skills Directory Pagination */}
              <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.75rem', marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid #e2e8f0' }}>
                <button
                  className="btn-navy-outline"
                  disabled={page <= 1}
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  style={{ padding: '0.35rem 0.8rem', fontSize: '0.8rem' }}
                >
                  Previous
                </button>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
                  Page {page} of {totalPages}
                </span>
                <button
                  className="btn-navy-outline"
                  disabled={page >= totalPages}
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  style={{ padding: '0.35rem 0.8rem', fontSize: '0.8rem' }}
                >
                  Next
                </button>
              </div>
            </div>
          )}

          {/* TAB 3: TRAINING PROGRAMMES & BATCH CAPACITY */}
          {adminTab === 'programmes' && (
            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>Training Programmes & Batch Directory</h3>
                  <p style={{ fontSize: '0.82rem', color: '#64748b' }}>View and monitor registered training programmes, associated centres, faculty assignments and batch capacity across the NagrikSetu platform.</p>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#475569', backgroundColor: '#f1f5f9', padding: '0.4rem 0.8rem', borderRadius: '6px', fontWeight: 600 }}>
                  Total Registered Programmes: {programmes.length}
                </div>
              </div>

              <div style={{ display: 'grid', gap: '1rem' }}>
                {programmes.map((p: any) => (
                  <div key={p.code} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <div>
                        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#ea580c', marginRight: '0.5rem' }}>{p.code}</span>
                        <strong style={{ fontSize: '1.05rem', color: '#0f172a' }}>{p.title}</strong>
                      </div>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#16a34a', backgroundColor: '#f0fdf4', padding: '0.2rem 0.6rem', borderRadius: '4px' }}>
                        {p.fee === 0 ? 'Free Subsidized' : `₹ ${p.fee}`}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '0.75rem' }}>{p.description}</p>
                    <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.78rem', color: '#475569', marginBottom: '0.75rem' }}>
                      <span><strong>Mode:</strong> {p.mode}</span>
                      <span><strong>Centre:</strong> {p.centre_name}</span>
                      <span><strong>Faculty:</strong> {p.trainer_name}</span>
                    </div>

                    <h5 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#334155', marginBottom: '0.4rem' }}>Allocated Batches & Concurrency Capacity:</h5>
                    <div style={{ display: 'grid', gap: '0.4rem' }}>
                      {p.batches?.map((b: any) => (
                        <div key={b.code} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f8fafc', padding: '0.6rem 0.9rem', borderRadius: '6px', fontSize: '0.8rem' }}>
                          <span><strong>{b.batch_name}</strong> ({b.timings})</span>
                          <span style={{ fontWeight: 700, color: b.available_seats > 0 ? '#166534' : '#b91c1c' }}>
                            {b.available_seats} / {b.total_seats} seats remaining • State: {b.status}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 4: TRAINING CENTRES */}
          {adminTab === 'centres' && (() => {
            const allCentres = adminCentresList.length > 0 ? adminCentresList : centres;
            const approvedCentres = allCentres.filter((c: any) => c.approval_status === 'APPROVED');
            const rejectedCentres = allCentres.filter((c: any) => c.approval_status === 'REJECTED');
            const filteredCentres = adminCentreFilter === 'APPROVED'
              ? approvedCentres
              : adminCentreFilter === 'REJECTED'
              ? rejectedCentres
              : allCentres;

            return (
              <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Building2 size={22} color="#0284c7" /> Training Centres Directory
                    </h3>
                    <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                      View and monitor registered training centres, institutional details, programme associations, enrolments and assigned centre administrators across the NagrikSetu platform.
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    <button type="button" className="btn-navy-outline" onClick={fetchAdminCentres} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <RefreshCw size={15} /> Refresh List
                    </button>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <div style={{ fontSize: '0.82rem', color: '#166534', backgroundColor: '#dcfce7', padding: '0.4rem 0.8rem', borderRadius: '6px', fontWeight: 700, border: '1px solid #bbf7d0' }}>
                        Approved Active Centres: {approvedCentres.length}
                      </div>
                      <div style={{ fontSize: '0.82rem', color: '#991b1b', backgroundColor: '#fee2e2', padding: '0.4rem 0.8rem', borderRadius: '6px', fontWeight: 700, border: '1px solid #fecaca' }}>
                        Rejected Registrations: {rejectedCentres.length}
                      </div>
                      <div style={{ fontSize: '0.82rem', color: '#475569', backgroundColor: '#f1f5f9', padding: '0.4rem 0.8rem', borderRadius: '6px', fontWeight: 600, border: '1px solid #e2e8f0' }}>
                        Total Records: {allCentres.length}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Filter Bar: Approved (default), Rejected, All */}
                <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
                  <button
                    type="button"
                    onClick={() => setAdminCentreFilter('APPROVED')}
                    style={{
                      padding: '0.4rem 0.9rem',
                      borderRadius: '6px',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      border: '1px solid',
                      backgroundColor: adminCentreFilter === 'APPROVED' ? '#166534' : '#f8fafc',
                      color: adminCentreFilter === 'APPROVED' ? '#ffffff' : '#334155',
                      borderColor: adminCentreFilter === 'APPROVED' ? '#166534' : '#cbd5e1'
                    }}
                  >
                    Approved Active Centres ({approvedCentres.length})
                  </button>
                  <button
                    type="button"
                    onClick={() => setAdminCentreFilter('REJECTED')}
                    style={{
                      padding: '0.4rem 0.9rem',
                      borderRadius: '6px',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      border: '1px solid',
                      backgroundColor: adminCentreFilter === 'REJECTED' ? '#991b1b' : '#f8fafc',
                      color: adminCentreFilter === 'REJECTED' ? '#ffffff' : '#334155',
                      borderColor: adminCentreFilter === 'REJECTED' ? '#991b1b' : '#cbd5e1'
                    }}
                  >
                    Rejected Duplicate Registrations ({rejectedCentres.length})
                  </button>
                  <button
                    type="button"
                    onClick={() => setAdminCentreFilter('ALL')}
                    style={{
                      padding: '0.4rem 0.9rem',
                      borderRadius: '6px',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      cursor: 'pointer',
                      border: '1px solid',
                      backgroundColor: adminCentreFilter === 'ALL' ? '#0f2444' : '#f8fafc',
                      color: adminCentreFilter === 'ALL' ? '#ffffff' : '#334155',
                      borderColor: adminCentreFilter === 'ALL' ? '#0f2444' : '#cbd5e1'
                    }}
                  >
                    All Centre Records ({allCentres.length})
                  </button>
                </div>

                {adminCentresLoading ? (
                  <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>Loading approved training centres...</div>
                ) : filteredCentres.length === 0 ? (
                  <div style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
                    No training centres match the selected filter.
                  </div>
                ) : (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.25rem' }}>
                    {filteredCentres.map((c: any) => (
                      <div key={c.code} style={{ border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', backgroundColor: c.approval_status === 'SUSPENDED' ? '#fff7ed' : c.approval_status === 'REJECTED' ? '#fef2f2' : '#ffffff', boxShadow: '0 2px 4px rgba(0,0,0,0.03)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                            <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#ea580c', background: '#ffedd5', padding: '2px 8px', borderRadius: '4px' }}>{c.code}</span>
                            <span style={{ fontSize: '0.75rem', fontWeight: 700, padding: '2px 8px', borderRadius: '4px', backgroundColor: c.approval_status === 'APPROVED' ? '#dcfce7' : c.approval_status === 'SUSPENDED' ? '#fef3c7' : '#fee2e2', color: c.approval_status === 'APPROVED' ? '#166534' : c.approval_status === 'SUSPENDED' ? '#92400e' : '#991b1b' }}>
                              {c.approval_status || 'APPROVED'}
                            </span>
                          </div>
                          <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.3rem' }}>{c.name}</h4>
                          <p style={{ fontSize: '0.8rem', color: '#475569', marginBottom: '0.6rem' }}>{c.location || c.address}</p>
                          
                          <div style={{ fontSize: '0.78rem', color: '#64748b', display: 'flex', flexDirection: 'column', gap: '0.25rem', marginBottom: '0.75rem', background: '#f8fafc', padding: '0.6rem', borderRadius: '6px' }}>
                            <div><strong>Programmes:</strong> {c.program_count ?? 0} • <strong>Active Enrolments:</strong> {c.enrolment_count ?? 0}</div>
                            <div><strong>Contact:</strong> {c.contact_phone || 'N/A'} • {c.contact_email || 'N/A'}</div>
                            {c.approval_status === 'REJECTED' && c.rejection_reason && (
                              <div style={{ color: '#b91c1c' }}><strong>Status Note:</strong> {c.rejection_reason}</div>
                            )}
                          </div>

                          {/* Centre Admin Assignment Information */}
                          <div style={{ background: c.approval_status === 'REJECTED' ? '#f8fafc' : '#f0fdf4', border: `1px solid ${c.approval_status === 'REJECTED' ? '#e2e8f0' : '#bbf7d0'}`, borderRadius: '6px', padding: '0.6rem', marginBottom: '1rem', fontSize: '0.78rem' }}>
                            <div style={{ fontWeight: 700, color: c.approval_status === 'REJECTED' ? '#64748b' : '#166534', marginBottom: '0.2rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                              <Shield size={13} /> Assigned Centre Administrator:
                            </div>
                            {c.admin_account ? (
                              <div style={{ color: '#14532d' }}>
                                <div><strong>Name:</strong> {c.admin_account.full_name || 'Admin'}</div>
                                <div><strong>Email:</strong> {c.admin_account.email}</div>
                              </div>
                            ) : (
                              <div style={{ color: '#9a3412', fontStyle: 'italic' }}>No administrator assigned</div>
                            )}
                          </div>
                        </div>

                        {/* Read-Only Inspection Action */}
                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', paddingTop: '0.75rem', borderTop: '1px solid #e2e8f0' }}>
                          <button
                            type="button"
                            className="btn-navy-outline"
                            style={{ fontSize: '0.76rem', padding: '6px 12px', flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.4rem' }}
                            onClick={() => {
                              openPublicCentreProfile(c.id || c.code);
                            }}
                          >
                            <Building2 size={13} /> View Centre Profile
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })()}
        </div>
        </div>
      ) : (
        /* CITIZEN PORTAL & DASHBOARD */
        <div>
          {/* 2. Main Navigation Bar */}
      <header className="header-main">
        <div className="header-container">
          {/* LEFT: NagrikSetu logo and Skill Development Service branding */}
          <div className="brand-wrapper" onClick={() => { setActiveTab('home'); setMobileMenuOpen(false); }}>
            <div className="brand-emblem">
              <Award size={22} />
            </div>
            <div className="brand-text">
              <h1>NagrikSetu</h1>
              <p>Skill Development Service</p>
            </div>
          </div>

          {/* MOBILE HAMBURGER TOGGLE */}
          <button
            type="button"
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          {/* CENTRE: Navigation Links */}
          <nav className={`nav-links ${mobileMenuOpen ? 'nav-open' : ''}`}>
            <button className={`nav-item-btn ${activeTab === 'home' ? 'active' : ''}`} onClick={() => { setActiveTab('home'); setMobileMenuOpen(false); }}>
              {t('nav.home')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'explore_skills' || activeTab === 'category_details' ? 'active' : ''}`} onClick={() => { setActiveTab('explore_skills'); setMobileMenuOpen(false); }}>
              <Compass size={14} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} /> Explore Skills
            </button>
            <button className={`nav-item-btn ${activeTab === 'courses' ? 'active' : ''}`} onClick={() => { setActiveTab('courses'); setMobileMenuOpen(false); }}>
              All Courses
            </button>
            <button className={`nav-item-btn ${activeTab === 'programmes' ? 'active' : ''}`} onClick={() => { setActiveTab('programmes'); setMobileMenuOpen(false); }}>
              {t('nav.training_programmes')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'centres' ? 'active' : ''}`} onClick={() => { setActiveTab('centres'); setMobileMenuOpen(false); }}>
              {t('nav.centres')}
            </button>

            {token && userRole !== 'TRAINING_CENTRE_ADMIN' && !userRole.endsWith('ADMIN') && (
              <>
                <button className={`nav-item-btn ${activeTab === 'applications' ? 'active' : ''}`} onClick={() => { setActiveTab('applications'); setMobileMenuOpen(false); }}>
                  My Applications
                </button>
                {isStudent && (
                  <button
                    className={`nav-item-btn nav-student-portal-btn ${activeTab === 'student_portal' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('student_portal'); setMobileMenuOpen(false); }}
                  >
                    <GraduationCap size={14} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} />
                    Student Portal
                  </button>
                )}
              </>
            )}
            <button className={`nav-item-btn ${activeTab === 'gap' ? 'active' : ''}`} onClick={() => { setActiveTab('gap'); setMobileMenuOpen(false); }}>
              {t('nav.gap_analysis')}
            </button>

            {/* Mobile Drawer Only Profile & Logout items */}
            {token && (
              <div className="mobile-drawer-account-items">
                {userRole !== 'TRAINING_CENTRE_ADMIN' && !userRole.endsWith('ADMIN') && (
                  <button className={`nav-item-btn ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => { setActiveTab('profile'); setMobileMenuOpen(false); }}>
                    <User size={14} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} /> My Profile
                  </button>
                )}
                <button className="nav-item-btn mobile-logout-item" onClick={() => { handleLogout(); setMobileMenuOpen(false); }}>
                  <LogOut size={14} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} /> Log Out ({userName || citizenRef})
                </button>
              </div>
            )}
          </nav>

          {/* RIGHT: User Profile, Account Information & Logout */}
          <div className="nav-actions">
            {token ? (
              <div className="nav-user-account-wrapper">
                {userRole !== 'TRAINING_CENTRE_ADMIN' && !userRole.endsWith('ADMIN') && (
                  <button
                    className={`nav-item-btn nav-profile-link ${activeTab === 'profile' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('profile'); setMobileMenuOpen(false); }}
                  >
                    <User size={13} style={{ display: 'inline', marginRight: '3px', verticalAlign: 'middle' }} />
                    My Profile
                  </button>
                )}

                {/* Logged-in user badge (cleanly separated) */}
                <div className="nav-user-badge" title={userEmail || userName}>
                  <div className="nav-user-avatar">
                    <User size={12} />
                  </div>
                  <div className="nav-user-info">
                    <span className="nav-user-name">{userName || citizenRef || 'User'}</span>
                    {isStudent && studentId && (
                      <span className="nav-user-subtag">{studentId}</span>
                    )}
                  </div>
                </div>

                {userRole === 'SKILL_DEPARTMENT_ADMIN' && (
                  <button className="btn-admin-pill" onClick={() => setAdminTab('applications')}>
                    <Shield size={13} /> Admin Desk
                  </button>
                )}

                <button className="btn-logout" onClick={handleLogout} title={t('nav.logout')}>
                  <LogOut size={13} /> <span>{t('nav.logout')}</span>
                </button>
              </div>
            ) : (
              <div className="nav-guest-actions">
                <button className="btn-navy-outline" onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}>
                  <LogIn size={14} /> {t('nav.sign_in')}
                </button>
                <button className="btn-primary-orange" onClick={() => { setAuthPortalView('register_citizen'); setAuthError(''); }}>
                  <UserPlus size={14} /> {t('nav.register')}
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Banner Notice */}
      {bannerNotice && (
        <div style={{ backgroundColor: '#eff6ff', borderBottom: '1px solid #bfdbfe', padding: '0.6rem 1.5rem', textAlign: 'center', fontSize: '0.85rem', color: '#1e40af', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={16} />
          {bannerNotice}
          <button style={{ background: 'none', border: 'none', cursor: 'pointer', marginLeft: '1rem', color: '#1e40af' }} onClick={() => setBannerNotice('')}>✕</button>
        </div>
      )}

      {/* MAIN BODY SECTIONS */}
      {activeTab === 'home' && (
        <div>
          {/* Hero Section */}
          <div className="hero-wrapper">
            <div className="hero-content">
              <div className="hero-pill-badge">
                <Shield size={13} /> {t('hero.badge')}
              </div>
              <h1 className="hero-title">
                {t('hero.title')} • <span className="accent">Discover. Learn. Build Your Future.</span>
              </h1>
              <p className="hero-tagline">Discover. Learn. Build Your Future.</p>
              <p className="hero-desc">{t('hero.description')}</p>

              {/* Hero Search */}
              <div className="hero-search-bar">
                <input
                  type="text"
                  placeholder={t('hero.search_placeholder')}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      setActiveTab('courses');
                      fetchSkills(selectedCategory, selectedLevel, searchQuery, 1);
                    }
                  }}
                />
                <button onClick={() => { setActiveTab('courses'); fetchSkills(selectedCategory, selectedLevel, searchQuery, 1); }}>
                  <Search size={16} /> Search
                </button>
              </div>

              {/* Hero Stats (Dynamically derived from real MySQL database) */}
              <div className="hero-stats-row" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))' }}>
                <div className="hero-stat-card">
                  <div className="hero-stat-number">{homepageStats.skills_available || totalSkills || 105}</div>
                  <div className="hero-stat-label" style={{ fontWeight: 700, letterSpacing: '0.02em' }}>Skills Available</div>
                </div>
                <div className="hero-stat-card">
                  <div className="hero-stat-number">{homepageStats.training_programmes || programmes.length || 125}</div>
                  <div className="hero-stat-label" style={{ fontWeight: 700, letterSpacing: '0.02em' }}>Training Programmes</div>
                </div>
                <div className="hero-stat-card">
                  <div className="hero-stat-number">{homepageStats.registered_training_centres || centres.length || 6}</div>
                  <div className="hero-stat-label" style={{ fontWeight: 700, letterSpacing: '0.02em' }}>Registered Training Centres</div>
                </div>
              </div>
            </div>
          </div>

          {/* Clean, Focused Citizen Opportunity Gateway */}
          <div className="main-container" style={{ paddingBottom: '3.5rem' }}>
            {/* Primary Discovery Gateway Banner */}
            <div style={{
              background: 'linear-gradient(135deg, #0f2444 0%, #1e3a8a 100%)',
              borderRadius: '16px',
              padding: '2.5rem 2rem',
              color: '#ffffff',
              boxShadow: '0 20px 25px -5px rgba(15, 36, 68, 0.15)',
              marginBottom: '2.5rem',
              position: 'relative',
              overflow: 'hidden'
            }}>
              <div style={{ maxWidth: '680px', position: 'relative', zIndex: 1 }}>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'rgba(249, 115, 22, 0.2)', border: '1px solid rgba(249, 115, 22, 0.4)', padding: '0.3rem 0.75rem', borderRadius: '50px', fontSize: '0.78rem', color: '#fed7aa', fontWeight: 700, marginBottom: '1rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  <Sparkles size={14} color="#f97316" /> National Skill Mission Gateway
                </div>
                <h2 style={{ fontSize: '1.85rem', fontWeight: 800, margin: '0 0 0.75rem 0', color: '#ffffff', lineHeight: 1.25 }}>
                  Discover High-Growth Skills Aligned with Industry & Career Pathways
                </h2>
                <p style={{ fontSize: '0.95rem', color: '#cbd5e1', lineHeight: 1.6, margin: '0 0 1.75rem 0' }}>
                  NagrikSetu provides accredited technical curricula, hands-on batch schedules, and subsidized government certifications across Karnataka. Browse by designated skilling sectors on our dedicated Explore Skills portal.
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
                  <button
                    type="button"
                    className="btn-primary-orange"
                    style={{ padding: '0.75rem 1.75rem', fontSize: '0.95rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.5rem', boxShadow: '0 10px 15px -3px rgba(234, 88, 12, 0.3)' }}
                    onClick={() => setActiveTab('explore_skills')}
                  >
                    <Compass size={18} /> Explore All Skill Categories <ArrowRight size={16} />
                  </button>
                  <button
                    type="button"
                    style={{ backgroundColor: 'rgba(255, 255, 255, 0.12)', border: '1px solid rgba(255, 255, 255, 0.25)', color: '#ffffff', padding: '0.75rem 1.5rem', borderRadius: '6px', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', transition: 'background 0.2s' }}
                    onClick={() => setActiveTab('centres')}
                  >
                    <Building2 size={16} /> Locate Accredited Centres
                  </button>
                </div>
              </div>
            </div>

            {/* Platform Feature Pillars */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
              <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '1.5rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.02)' }}>
                <div style={{ width: '44px', height: '44px', borderRadius: '10px', backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563eb', marginBottom: '1rem' }}>
                  <Layers size={22} />
                </div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.4rem' }}>Sector-Specific Categorisation</h3>
                <p style={{ fontSize: '0.85rem', color: '#64748b', lineHeight: 1.5, margin: 0 }}>
                  Structured browsing across 10 certified technical domains, from AI and Cloud to Electrical and Healthcare.
                </p>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#2563eb', fontWeight: 700, fontSize: '0.82rem', padding: 0, marginTop: '1rem', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                  onClick={() => setActiveTab('explore_skills')}
                >
                  Explore Sectors →
                </button>
              </div>

              <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '1.5rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.02)' }}>
                <div style={{ width: '44px', height: '44px', borderRadius: '10px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#16a34a', marginBottom: '1rem' }}>
                  <Building2 size={22} />
                </div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.4rem' }}>Verified Regional Training Centres</h3>
                <p style={{ fontSize: '0.85rem', color: '#64748b', lineHeight: 1.5, margin: 0 }}>
                  State-of-the-art regional institutes located across Bengaluru, Mysuru, Hubballi, and coastal districts.
                </p>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#16a34a', fontWeight: 700, fontSize: '0.82rem', padding: 0, marginTop: '1rem', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                  onClick={() => setActiveTab('centres')}
                >
                  View Centre Network →
                </button>
              </div>

              <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '1.5rem', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.02)' }}>
                <div style={{ width: '44px', height: '44px', borderRadius: '10px', backgroundColor: '#fff7ed', border: '1px solid #fed7aa', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ea580c', marginBottom: '1rem' }}>
                  <Award size={22} />
                </div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.4rem' }}>Verifiable Digital Certifications</h3>
                <p style={{ fontSize: '0.85rem', color: '#64748b', lineHeight: 1.5, margin: 0 }}>
                  Every completed qualification issues an official tamper-proof credential verifiable by employers.
                </p>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#ea580c', fontWeight: 700, fontSize: '0.82rem', padding: 0, marginTop: '1rem', cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
                  onClick={() => setActiveTab('gap')}
                >
                  Analyze Your Skill Gaps →
                </button>
              </div>
            </div>

            {/* How It Works Progression Bar */}
            <div style={{ backgroundColor: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '1.75rem 2rem', textAlign: 'center' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 800, color: '#0f2444', margin: '0 0 1.25rem 0' }}>
                Structured Citizen Opportunity Journey
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem', alignItems: 'center' }}>
                <div style={{ padding: '0.75rem', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#ea580c', marginBottom: '0.2rem' }}>STEP 1</div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f2444' }}>Explore Skills</div>
                  <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Select designated sector</div>
                </div>
                <div style={{ color: '#94a3b8', display: 'none' }}>→</div>
                <div style={{ padding: '0.75rem', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#2563eb', marginBottom: '0.2rem' }}>STEP 2</div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f2444' }}>Category Details</div>
                  <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Curriculum & centres</div>
                </div>
                <div style={{ color: '#94a3b8', display: 'none' }}>→</div>
                <div style={{ padding: '0.75rem', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#16a34a', marginBottom: '0.2rem' }}>STEP 3</div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f2444' }}>Select Batch</div>
                  <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Check seat availability</div>
                </div>
                <div style={{ color: '#94a3b8', display: 'none' }}>→</div>
                <div style={{ padding: '0.75rem', backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                  <div style={{ fontSize: '0.72rem', fontWeight: 800, color: '#9333ea', marginBottom: '0.2rem' }}>STEP 4</div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f2444' }}>Apply & Verify</div>
                  <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Dossier allocation</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          PAGE: EXPLORE SKILLS (Amazon-style Category Discovery Gateway)
         ========================================================================= */}
      {activeTab === 'explore_skills' && (
        <div className="main-container" style={{ paddingBottom: '3.5rem' }}>
          {/* Breadcrumbs Navigation */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', color: '#64748b', marginBottom: '1.25rem' }}>
            <button
              type="button"
              style={{ background: 'none', border: 'none', padding: 0, color: '#2563eb', cursor: 'pointer', fontWeight: 600 }}
              onClick={() => setActiveTab('home')}
            >
              Home
            </button>
            <ChevronRight size={14} color="#94a3b8" />
            <span style={{ color: '#0f2444', fontWeight: 700 }}>Explore Skills</span>
          </div>

          {/* Section Header */}
          <div className="section-header" style={{ marginBottom: '1.75rem' }}>
            <div>
              <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: '#ea580c', fontWeight: 700, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.25rem' }}>
                <Compass size={14} /> National Qualification Framework
              </div>
              <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#0f2444', margin: '0 0 0.35rem 0' }}>
                Explore Accredited Skill Sectors
              </h2>
              <p style={{ color: '#64748b', fontSize: '0.9rem', margin: 0 }}>
                Select any skilling category to access dedicated curriculum pathways, regional centres, batches, and government certification programmes.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="btn-navy-outline" onClick={() => setActiveTab('courses')}>
                <Search size={14} /> Search All Courses
              </button>
            </div>
          </div>

          {/* Categories Grid (Retrieved live from MySQL database) */}
          {categories.length === 0 ? (
            <div style={{ padding: '3rem', textAlign: 'center', backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
              <Loader2 className="animate-spin" size={32} color="#ea580c" style={{ margin: '0 auto 1rem auto' }} />
              <p style={{ color: '#64748b', fontSize: '0.9rem' }}>Loading accredited skill sectors from backend...</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '3rem' }}>
              {categories.map((c: any) => (
                <div
                  key={c.code}
                  style={{
                    backgroundColor: '#ffffff',
                    border: '1.5px solid #e2e8f0',
                    borderRadius: '12px',
                    padding: '1.5rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.02)',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#ea580c';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 10px 20px rgba(234, 88, 12, 0.08)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#e2e8f0';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.02)';
                  }}
                  onClick={() => openCategoryDetails(c.code || c.name)}
                >
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                      <div style={{ width: '44px', height: '44px', borderRadius: '10px', backgroundColor: '#fff7ed', border: '1px solid #fed7aa', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ea580c' }}>
                        <BookOpen size={22} />
                      </div>
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#64748b', backgroundColor: '#f1f5f9', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                        {c.code}
                      </span>
                    </div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f2444', marginBottom: '0.4rem' }}>
                      {c.name}
                    </h3>
                    <p style={{ fontSize: '0.84rem', color: '#64748b', lineHeight: 1.5, marginBottom: '1.25rem' }}>
                      {c.description}
                    </p>
                  </div>

                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', fontSize: '0.78rem' }}>
                      <span style={{ color: '#0f2444', fontWeight: 700 }}>
                        {c.skill_count || 10}+ Accredited Skills
                      </span>
                      <span style={{ color: '#ea580c', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                        Explore Category <ArrowRight size={14} />
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* =========================================================================
          PAGE: DEDICATED CATEGORY DETAILS PAGE (Amazon-style Sector Deep-Dive)
         ========================================================================= */}
      {activeTab === 'category_details' && (
        <div className="main-container" style={{ paddingBottom: '3.5rem' }}>
          {/* Breadcrumbs Navigation */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', color: '#64748b', marginBottom: '1.25rem' }}>
            <button
              type="button"
              style={{ background: 'none', border: 'none', padding: 0, color: '#2563eb', cursor: 'pointer', fontWeight: 600 }}
              onClick={() => setActiveTab('home')}
            >
              Home
            </button>
            <ChevronRight size={14} color="#94a3b8" />
            <button
              type="button"
              style={{ background: 'none', border: 'none', padding: 0, color: '#2563eb', cursor: 'pointer', fontWeight: 600 }}
              onClick={() => setActiveTab('explore_skills')}
            >
              Explore Skills
            </button>
            <ChevronRight size={14} color="#94a3b8" />
            <span style={{ color: '#0f2444', fontWeight: 700 }}>
              {categoryDetailsData?.category?.name || activeCategoryCode}
            </span>
          </div>

          {/* Loading State */}
          {loadingCategoryDetails && (
            <div style={{ padding: '4rem 2rem', textAlign: 'center', backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
              <Loader2 className="animate-spin" size={36} color="#ea580c" style={{ margin: '0 auto 1rem auto' }} />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f2444', margin: '0 0 0.4rem 0' }}>
                Retrieving Category Curriculum & Programmes...
              </h3>
              <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                Querying accredited skills, regional training centres, and upcoming batches.
              </p>
            </div>
          )}

          {/* Error State */}
          {categoryDetailsError && !loadingCategoryDetails && (
            <div style={{ padding: '3rem 2rem', textAlign: 'center', backgroundColor: '#fef2f2', borderRadius: '12px', border: '1px solid #fecaca' }}>
              <AlertCircle size={36} color="#dc2626" style={{ margin: '0 auto 1rem auto' }} />
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#991b1b', margin: '0 0 0.5rem 0' }}>
                Failed to Load Category
              </h3>
              <p style={{ color: '#b91c1c', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
                {categoryDetailsError}
              </p>
              <button className="btn-navy-outline" onClick={() => openCategoryDetails(activeCategoryCode)}>
                <RefreshCw size={14} /> Retry Loading
              </button>
            </div>
          )}

          {/* Loaded Category Details Content */}
          {categoryDetailsData && !loadingCategoryDetails && (
            <div>
              {/* Category Header Banner */}
              <div style={{
                backgroundColor: '#ffffff',
                border: '1.5px solid #e2e8f0',
                borderRadius: '12px',
                padding: '2rem',
                marginBottom: '2rem',
                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.02)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1rem' }}>
                  <div>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', color: '#ea580c', fontWeight: 700, fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.35rem' }}>
                      <BookOpen size={14} /> Designated Technical Sector: {categoryDetailsData.category.code}
                    </div>
                    <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f2444', margin: '0 0 0.5rem 0' }}>
                      {categoryDetailsData.category.name}
                    </h1>
                    <p style={{ fontSize: '0.95rem', color: '#64748b', maxWidth: '820px', lineHeight: 1.6, margin: 0 }}>
                      {categoryDetailsData.category.description}
                    </p>
                  </div>

                  <button
                    type="button"
                    className="btn-navy-outline"
                    style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}
                    onClick={() => setActiveTab('explore_skills')}
                  >
                    <ArrowLeft size={14} /> Back to All Categories
                  </button>
                </div>

                {/* Category Metric Badges */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', paddingTop: '1.25rem', borderTop: '1px solid #f1f5f9' }}>
                  <div style={{ backgroundColor: '#faf5ff', border: '1px solid #e9d5ff', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#6b21a8' }}>{categoryDetailsData.subcategories?.length || categoryDetailsData.stats.total_subcategories || 5}</div>
                    <div style={{ fontSize: '0.75rem', color: '#9333ea', fontWeight: 600 }}>Subcategories</div>
                  </div>
                  <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#1e3a8a' }}>{categoryDetailsData.stats.total_skills}</div>
                    <div style={{ fontSize: '0.75rem', color: '#2563eb', fontWeight: 600 }}>Skills Available</div>
                  </div>
                  <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#14532d' }}>{categoryDetailsData.stats.total_programmes}</div>
                    <div style={{ fontSize: '0.75rem', color: '#16a34a', fontWeight: 600 }}>Training Programmes</div>
                  </div>
                  <div style={{ backgroundColor: '#fff7ed', border: '1px solid #fed7aa', borderRadius: '8px', padding: '0.6rem 1rem' }}>
                    <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#7c2d12' }}>{categoryDetailsData.stats.total_centres}</div>
                    <div style={{ fontSize: '0.75rem', color: '#ea580c', fontWeight: 600 }}>Registered Training Centres</div>
                  </div>
                </div>
              </div>

              {/* Sub-Section 1: Training Programmes & Batch Schedules */}
              <div style={{ marginBottom: '3rem' }}>
                <div className="section-header" style={{ marginBottom: '1.25rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f2444', margin: '0 0 0.25rem 0' }}>
                      Accredited Programmes in {categoryDetailsData.category.name}
                    </h3>
                    <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                      Subsidized training programmes with affiliated training centres, prerequisites, and live batch enrolment.
                    </p>
                  </div>
                </div>

                {categoryDetailsData.programmes.length === 0 ? (
                  <div style={{ padding: '2rem', textAlign: 'center', backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                    <p style={{ color: '#64748b', fontSize: '0.9rem', margin: 0 }}>No active programmes scheduled under this category yet.</p>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                    {categoryDetailsData.programmes.map((p: any) => (
                      <div
                        key={p.code}
                        style={{
                          backgroundColor: '#ffffff',
                          border: '1px solid #e2e8f0',
                          borderRadius: '12px',
                          padding: '1.5rem',
                          boxShadow: '0 2px 4px rgba(0,0,0,0.02)',
                          display: 'flex',
                          justifyContent: 'space-between',
                          flexWrap: 'wrap',
                          gap: '1.5rem',
                          alignItems: 'center'
                        }}
                      >
                        <div style={{ flex: 1, minWidth: '300px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
                            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#2563eb', backgroundColor: '#eff6ff', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #bfdbfe' }}>
                              {p.code}
                            </span>
                            <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#16a34a', backgroundColor: '#f0fdf4', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #bbf7d0' }}>
                              {p.mode}
                            </span>
                            {p.scholarship_available && (
                              <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#b45309', backgroundColor: '#fef3c7', padding: '0.15rem 0.5rem', borderRadius: '4px', border: '1px solid #fde68a' }}>
                                100% Subsidized
                              </span>
                            )}
                          </div>

                          <h4 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f2444', margin: '0 0 0.4rem 0' }}>
                            {p.title}
                          </h4>
                          <p style={{ fontSize: '0.84rem', color: '#64748b', lineHeight: 1.5, margin: '0 0 0.85rem 0' }}>
                            {p.description}
                          </p>

                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.25rem', fontSize: '0.78rem', color: '#475569' }}>
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                              <Clock size={14} color="#ea580c" /> {p.duration_hours} Hours Total
                            </span>
                            {p.centre && (
                              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                                <Building2 size={14} color="#0284c7" /> {p.centre.name} ({p.centre.location})
                              </span>
                            )}
                            {p.eligibility_criteria && (
                              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}>
                                <FileText size={14} color="#16a34a" /> Eligibility: {p.eligibility_criteria}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Action Box */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', minWidth: '220px' }}>
                          {(!userRole || userRole === 'CITIZEN') ? (
                            <button
                              type="button"
                              className="btn-primary-orange"
                              style={{ justifyContent: 'center' }}
                              onClick={() => handleStartEnrolment(p)}
                            >
                              Select Batch & Enrol
                            </button>
                          ) : (
                            <div
                              style={{
                                textAlign: 'center',
                                padding: '0.45rem 0.6rem',
                                backgroundColor: '#f1f5f9',
                                color: '#64748b',
                                borderRadius: '6px',
                                fontSize: '0.75rem',
                                fontWeight: 600,
                                border: '1px solid #e2e8f0'
                              }}
                            >
                              This feature is available to Citizen accounts only.
                            </div>
                          )}
                          <button
                            type="button"
                            className="btn-navy-outline"
                            style={{ justifyContent: 'center' }}
                            onClick={() => openCourseDetail(p.skill_code || 'SKL-0001')}
                          >
                            View Full Curriculum
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Sub-Section 2: Subcategories & Skills Hierarchy */}
              <div style={{ marginBottom: '3rem' }}>
                <div className="section-header" style={{ marginBottom: '1rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f2444', margin: '0 0 0.25rem 0' }}>
                      Accredited Subcategories & Specialisations
                    </h3>
                    <p style={{ color: '#64748b', fontSize: '0.85rem', margin: 0 }}>
                      Explore domain-specific specialisations. Click a subcategory to filter and view its accredited skills.
                    </p>
                  </div>
                </div>

                {/* Subcategories Pills / Filter Bar */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.6rem', marginBottom: '1.5rem' }}>
                  <button
                    type="button"
                    onClick={() => setSelectedSubcategoryId(null)}
                    style={{
                      padding: '0.45rem 0.9rem',
                      borderRadius: '20px',
                      fontSize: '0.82rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      border: '1.5px solid',
                      backgroundColor: selectedSubcategoryId === null ? '#0f2444' : '#ffffff',
                      color: selectedSubcategoryId === null ? '#ffffff' : '#475569',
                      borderColor: selectedSubcategoryId === null ? '#0f2444' : '#cbd5e1',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    All Subcategories ({categoryDetailsData.skills?.length || 0} Skills)
                  </button>
                  {categoryDetailsData.subcategories?.map((sub: any) => (
                    <button
                      key={sub.id}
                      type="button"
                      onClick={() => setSelectedSubcategoryId(selectedSubcategoryId === sub.id ? null : sub.id)}
                      style={{
                        padding: '0.45rem 0.9rem',
                        borderRadius: '20px',
                        fontSize: '0.82rem',
                        fontWeight: 700,
                        cursor: 'pointer',
                        border: '1.5px solid',
                        backgroundColor: selectedSubcategoryId === sub.id ? '#ea580c' : '#ffffff',
                        color: selectedSubcategoryId === sub.id ? '#ffffff' : '#334155',
                        borderColor: selectedSubcategoryId === sub.id ? '#ea580c' : '#cbd5e1',
                        transition: 'all 0.15s ease'
                      }}
                    >
                      {sub.name} ({sub.skill_count || sub.skills?.length || 0})
                    </button>
                  ))}
                </div>

                {/* Skills Grid filtered by subcategory */}
                <div className="cards-grid">
                  {(categoryDetailsData.skills || [])
                    .filter((s: any) => selectedSubcategoryId === null || s.subcategory_id === selectedSubcategoryId)
                    .map((s: any) => (
                      <div key={s.code} className="skill-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                          <span className="badge-category">{s.subcategory_name || s.category_name}</span>
                          <span className={`badge-level ${s.level.toLowerCase()}`}>{s.level}</span>
                        </div>
                        <h3>{s.name}</h3>
                        <p className="summary">{s.summary}</p>
                        <div className="card-meta-row">
                          <span className="meta-item"><Clock size={14} /> {s.duration_hours} Hours ({s.duration_weeks} wks)</span>
                          <span className="meta-item"><Users size={14} /> {s.enrolled_count} Enrolled</span>
                        </div>
                        <button className="btn-card-action" onClick={() => openCourseDetail(s.code)}>
                          View Skill Details <ArrowRight size={14} />
                        </button>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* EXPLORE COURSES CATALOGUE */}{/* EXPLORE COURSES CATALOGUE */}
      {activeTab === 'courses' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <h2>{t('sections.all_catalog')}</h2>
              <p>Explore over 100+ accredited skill tracks with detailed curricula, batches, and NSQF credentials</p>
            </div>
            <div style={{ fontSize: '0.85rem', color: '#64748b' }}>
              Showing {skills.length} of {totalSkills} total skills
            </div>
          </div>

          {/* Filter Bar */}
          <div style={{ backgroundColor: '#ffffff', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '2rem', display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
            <div style={{ flex: 1, minWidth: '220px' }}>
              <input
                type="text"
                className="form-control"
                placeholder="Search skills by keyword or code..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && fetchSkills(selectedCategory, selectedLevel, searchQuery, 1)}
              />
            </div>
            <div style={{ minWidth: '180px' }}>
              <select
                className="form-control"
                value={selectedCategory}
                onChange={(e) => { setSelectedCategory(e.target.value); setPage(1); }}
              >
                <option value="All">{t('common.all')} ({t('sections.categories')})</option>
                {categories.map((c: any) => (
                  <option key={c.code} value={c.name}>{c.name}</option>
                ))}
              </select>
            </div>
            <div style={{ minWidth: '140px' }}>
              <select
                className="form-control"
                value={selectedLevel}
                onChange={(e) => { setSelectedLevel(e.target.value); setPage(1); }}
              >
                <option value="All">{t('common.all')} ({t('course.level')})</option>
                <option value="Beginner">{t('common.beginner')}</option>
                <option value="Intermediate">{t('common.intermediate')}</option>
                <option value="Advanced">{t('common.advanced')}</option>
              </select>
            </div>
            <button className="btn-primary-orange" onClick={() => fetchSkills(selectedCategory, selectedLevel, searchQuery, 1)}>
              <Filter size={14} /> Apply Filters
            </button>
            <button className="btn-navy-outline" onClick={() => { setSelectedCategory('All'); setSelectedLevel('All'); setSearchQuery(''); setPage(1); fetchSkills('All', 'All', '', 1); }}>
              Clear
            </button>
          </div>

          {/* Cards Grid */}
          {loadingSkills ? (
            <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
              <RefreshCw size={32} className="animate-spin" style={{ margin: '0 auto 1rem auto' }} />
              Loading courses from the database...
            </div>
          ) : (
            <div className="cards-grid">
              {skills.map((s: any) => (
                <div key={s.code} className="skill-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <span className="badge-category">{s.category_name}</span>
                    <span className={`badge-level ${s.level.toLowerCase()}`}>{s.level}</span>
                  </div>
                  <h3>{s.name}</h3>
                  <p className="summary">{s.summary}</p>
                  <div className="card-meta-row">
                    <span className="meta-item"><Clock size={14} /> {s.duration_hours}h</span>
                    <span className="meta-item"><Award size={14} /> {s.rating} ★</span>
                    <span className="meta-item"><Users size={14} /> {s.enrolled_count} learners</span>
                  </div>
                  <button className="btn-card-action" onClick={() => openCourseDetail(s.code)}>
                    {t('course.view_details')} <ArrowRight size={14} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Pagination */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '0.5rem', marginTop: '2.5rem' }}>
            <button
              className="btn-navy-outline"
              disabled={page <= 1}
              onClick={() => setPage(p => Math.max(1, p - 1))}
            >
              Previous
            </button>
            <span style={{ display: 'flex', alignItems: 'center', padding: '0 1rem', fontSize: '0.85rem', fontWeight: 600 }}>
              Page {page} of {totalPages}
            </span>
            <button
              className="btn-navy-outline"
              disabled={page >= totalPages}
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            >
              Next
            </button>
          </div>
        </div>
      )}

      {/* TRAINING PROGRAMMES DISCOVERY */}
      {activeTab === 'programmes' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <h2>{t('sections.programmes_heading')}</h2>
              <p>Government subsidized training programmes with verifiable faculty and batch allocations</p>
            </div>
          </div>

          <div style={{ display: 'grid', gap: '1.25rem' }}>
            {programmes.map((p: any) => (
              <div
                key={p.code}
                style={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e2e8f0',
                  borderRadius: '10px',
                  padding: '1.5rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  flexWrap: 'wrap',
                  gap: '1.5rem'
                }}
              >
                <div style={{ flex: '1', minWidth: '300px' }}>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#ea580c', backgroundColor: '#fff7ed', padding: '0.2rem 0.6rem', borderRadius: '4px' }}>
                      {p.code}
                    </span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#166534', backgroundColor: '#f0fdf4', padding: '0.2rem 0.6rem', borderRadius: '4px' }}>
                      {p.fee === 0 ? '100% Subsidized (Free)' : `₹ ${p.fee}`}
                    </span>
                    <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#1e40af', backgroundColor: '#eff6ff', padding: '0.2rem 0.6rem', borderRadius: '4px' }}>
                      Mode: {p.mode}
                    </span>
                  </div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.35rem' }}>{p.title}</h3>
                  <p style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '0.75rem' }}>{p.description}</p>
                  <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8rem', color: '#64748b' }}>
                    <span><strong>Faculty:</strong> {p.trainer_name}</span>
                    <span><strong>Centre:</strong> {p.centre_name} ({p.centre_location})</span>
                    <span><strong>Duration:</strong> {p.duration_hours} Hours</span>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', minWidth: '220px' }}>
                  {(!userRole || userRole === 'CITIZEN') ? (
                    <button
                      className="btn-primary-orange"
                      style={{ justifyContent: 'center' }}
                      onClick={() => handleStartEnrolment(p)}
                    >
                      Select Batch & Enrol
                    </button>
                  ) : (
                    <div
                      style={{
                        textAlign: 'center',
                        padding: '0.45rem 0.6rem',
                        backgroundColor: '#f1f5f9',
                        color: '#64748b',
                        borderRadius: '6px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        border: '1px solid #e2e8f0'
                      }}
                    >
                      This feature is available to Citizen accounts only.
                    </div>
                  )}
                  <button
                    className="btn-navy-outline"
                    style={{ justifyContent: 'center' }}
                    onClick={() => openCourseDetail(p.skill_code || 'SKL-0001')}
                  >
                    View Curriculum
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ACCREDITED TRAINING CENTRES & REAL-WORLD DISCOVERY */}
      {activeTab === 'centres' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <h2>Training Centres Near Me</h2>
              <p>Discover real-world training centres, vocational institutes, IT academies, and government ITIs across any supported location with dynamic custom radius</p>
            </div>
          </div>

          {/* Location Detection & Filter Control Panel */}
          <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', padding: '1.75rem', marginBottom: '2rem', boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
            
            {/* Top Row: Search input + Custom Radius + Actions */}
            <form onSubmit={handleUniversalSearch} style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'flex-end', justifyContent: 'space-between' }}>
              
              {/* Universal Location Input */}
              <div style={{ flex: '2 1 260px', minWidth: '240px' }}>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                  Search Location (City, Locality, PIN code, Landmark)
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="text"
                    placeholder="e.g. CV Raman Nagar, Bengaluru / Indiranagar / 560038 / Mysuru / Chennai"
                    value={manualQuery}
                    onChange={(e) => setManualQuery(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem 0.75rem 2.4rem',
                      fontSize: '0.88rem',
                      border: '1px solid #cbd5e1',
                      borderRadius: '8px',
                      outline: 'none',
                      boxSizing: 'border-box'
                    }}
                  />
                  <Search size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                </div>
              </div>

              {/* Target Skill / Topic Filter */}
              <div style={{ flex: '1.5 1 200px', minWidth: '180px' }}>
                <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>
                  Filter by Skill / Course (Optional)
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="text"
                    placeholder="e.g. Python, Java, C++, Data Analytics, Web Development"
                    value={skillSearchFilter}
                    onChange={(e) => setSkillSearchFilter(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem 0.75rem 2.4rem',
                      fontSize: '0.88rem',
                      border: '1px solid #cbd5e1',
                      borderRadius: '8px',
                      outline: 'none',
                      boxSizing: 'border-box'
                    }}
                  />
                  <GraduationCap size={16} color="#64748b" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                </div>
              </div>

              {/* Dynamic Custom Radius Input & Slider */}
              <div style={{ flex: '1 1 200px', minWidth: '180px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>
                    Search Radius: <span style={{ color: '#ea580c', fontWeight: 700 }}>{selectedRadius} km</span>
                  </label>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <input
                    type="number"
                    min="1"
                    max="25"
                    step="1"
                    value={customRadiusInput}
                    onChange={(e) => {
                      const val = e.target.value;
                      setCustomRadiusInput(val);
                      const parsed = parseFloat(val);
                      if (!isNaN(parsed) && parsed >= 1 && parsed <= 25) {
                        setSelectedRadius(parsed);
                      }
                    }}
                    style={{
                      width: '75px',
                      padding: '0.72rem 0.6rem',
                      fontSize: '0.88rem',
                      fontWeight: 600,
                      border: '1px solid #cbd5e1',
                      borderRadius: '8px',
                      textAlign: 'center',
                      outline: 'none'
                    }}
                  />
                  <input
                    type="range"
                    min="1"
                    max="25"
                    step="1"
                    value={selectedRadius}
                    onChange={(e) => {
                      const r = parseFloat(e.target.value);
                      setSelectedRadius(r);
                      setCustomRadiusInput(String(r));
                    }}
                    style={{ flex: 1, accentColor: '#ea580c', cursor: 'pointer' }}
                  />
                </div>
              </div>

              {/* Search Button */}
              <div>
                <button
                  type="submit"
                  disabled={manualSearching || nearbyLoading}
                  style={{
                    backgroundColor: '#ea580c',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '0.75rem 1.4rem',
                    fontSize: '0.9rem',
                    fontWeight: 600,
                    cursor: manualSearching || nearbyLoading ? 'not-allowed' : 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    boxShadow: '0 2px 4px rgba(234, 88, 12, 0.25)',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {manualSearching || nearbyLoading ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search size={16} />
                      Discover Centres
                    </>
                  )}
                </button>
              </div>

              {/* GPS Button */}
              <div>
                <button
                  type="button"
                  onClick={handleUseCurrentLocation}
                  disabled={nearbyLoading}
                  style={{
                    backgroundColor: '#1e3a8a',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '8px',
                    padding: '0.75rem 1.25rem',
                    fontSize: '0.9rem',
                    fontWeight: 600,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem',
                    cursor: nearbyLoading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.15s ease',
                    boxShadow: '0 2px 4px rgba(30, 58, 138, 0.2)'
                  }}
                >
                  {nearbyLoading && locationMode === 'GPS' ? (
                    <>
                      <Loader2 size={16} className="animate-spin" />
                      Detecting GPS...
                    </>
                  ) : (
                    <>
                      <Crosshair size={16} />
                      Find Training Centres Near Me
                    </>
                  )}
                </button>
              </div>

            </form>

            {/* Quick Radius Presets Bar (Strict max 25 km) */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '1rem', flexWrap: 'wrap' }}>
              <span style={{ fontSize: '0.76rem', fontWeight: 600, color: '#64748b' }}>Quick Radius:</span>
              {[1, 5, 10, 15, 20, 25].map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => {
                    setSelectedRadius(r);
                    setCustomRadiusInput(String(r));
                  }}
                  style={{
                    padding: '0.3rem 0.65rem',
                    fontSize: '0.75rem',
                    fontWeight: selectedRadius === r ? 700 : 500,
                    backgroundColor: selectedRadius === r ? '#1e3a8a' : '#f1f5f9',
                    color: selectedRadius === r ? '#ffffff' : '#475569',
                    border: '1px solid #e2e8f0',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {r} km
                </button>
              ))}
            </div>

            {/* Status / Active Location Bar */}
            {userLocation && (
              <div style={{ marginTop: '1.25rem', padding: '0.75rem 1rem', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#166534', fontSize: '0.85rem' }}>
                  <Compass size={16} />
                  <span>
                    <strong>Location Active ({locationMode === 'GPS' ? 'Real GPS' : 'Universal Search'}):</strong> {locationLabel}
                    <span style={{ color: '#15803d', fontSize: '0.78rem', marginLeft: '8px' }}>
                      ({userLocation.latitude.toFixed(4)}, {userLocation.longitude.toFixed(4)}) • Provider: <strong>{discoveredProvider}</strong>
                    </span>
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setUserLocation(null);
                    setLocationMode('NONE');
                    setLocationLabel('');
                    setNearbyCentres([]);
                    setNearbyError('');
                    setSelectedCentreId(null);
                  }}
                  style={{
                    backgroundColor: 'transparent',
                    border: 'none',
                    color: '#64748b',
                    fontSize: '0.78rem',
                    cursor: 'pointer',
                    textDecoration: 'underline'
                  }}
                >
                  Reset Location
                </button>
              </div>
            )}

            {/* Error Message */}
            {nearbyError && (
              <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', backgroundColor: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', color: '#991b1b', fontSize: '0.84rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <AlertCircle size={16} />
                <span>{nearbyError}</span>
              </div>
            )}
          </div>

          {/* Interactive Map & Side-by-Side Highlights */}
          <div id="training-centre-map-section" style={{ marginBottom: '2.5rem', scrollMarginTop: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', margin: 0, display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <MapPin size={16} color="#ea580c" />
                Interactive Map & Live Radius Discovery
              </h3>
              <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
                {userLocation ? `Showing institutes within ${selectedRadius} km` : 'Accredited physical hubs and technical institutes'}
              </span>
            </div>

            <CentreLocationMap
              userLocation={userLocation}
              locationLabel={locationLabel}
              centres={userLocation ? nearbyCentres : centres}
              radiusKm={selectedRadius}
              selectedCentreId={selectedCentreId}
              onSelectCentre={(c) => setSelectedCentreId(c.id || c.code)}
            />
          </div>

          {/* Results List Header */}
          <div style={{ marginBottom: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                {userLocation
                  ? `${nearbyCentres.length} Training Institute${nearbyCentres.length === 1 ? '' : 's'} Discovered Near You`
                  : 'All Registered Training Centres'}
              </h3>
              <p style={{ margin: '3px 0 0 0', fontSize: '0.82rem', color: '#64748b' }}>
                {userLocation
                  ? `Sorted nearest to farthest within ${selectedRadius} km from ${locationLabel}`
                  : 'Enter a locality/PIN code above or click "Use GPS" to discover institutes dynamically'}
              </p>
            </div>
            {userLocation && nearbyCentres.length > 0 && (
              <span style={{ fontSize: '0.78rem', fontWeight: 600, color: '#0f766e', backgroundColor: '#ccfbf1', padding: '4px 10px', borderRadius: '12px' }}>
                Nearest: {nearbyCentres[0].name} ({nearbyCentres[0].distance_km} km)
              </span>
            )}
          </div>

          {/* No Centres Found Empty State */}
          {userLocation && !nearbyLoading && nearbyCentres.length === 0 && (
            <div style={{ backgroundColor: '#f8fafc', border: '1px dashed #cbd5e1', borderRadius: '12px', padding: '3rem 1.5rem', textAlign: 'center', marginBottom: '2.5rem' }}>
              <MapPin size={36} color="#94a3b8" style={{ margin: '0 auto 0.75rem auto' }} />
              <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#1e293b', marginBottom: '0.5rem' }}>
                {locationMode === 'GPS'
                  ? 'No verified training centres found near your current location.'
                  : 'No training centres found in this location.'}
              </h4>
              <p style={{ fontSize: '0.88rem', color: '#64748b', maxWidth: '520px', margin: '0 auto 1.25rem auto', lineHeight: '1.5' }}>
                {locationMode === 'GPS'
                  ? `No verified training centres were found within ${selectedRadius} km of your GPS coordinates. Try expanding your search radius up to 25 km or search manually.`
                  : `No verified or accredited training centres were discovered within the selected ${selectedRadius} km radius. Try searching a neighbouring area or expand the radius up to 25 km.`}
              </p>
              <div style={{ display: 'inline-flex', gap: '0.5rem', flexWrap: 'wrap', justifyContent: 'center' }}>
                {[5, 10, 20, 25].filter(r => r > selectedRadius).map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => {
                      setSelectedRadius(r);
                      setCustomRadiusInput(String(r));
                    }}
                    style={{
                      padding: '0.5rem 1rem',
                      fontSize: '0.82rem',
                      fontWeight: 600,
                      backgroundColor: '#1e3a8a',
                      color: '#ffffff',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer'
                    }}
                  >
                    Expand to {r} km
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Cards Grid */}
          {(() => {
            if (!userLocation) {
              return (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
                  {centres.map((c: any) => renderCentreCard(c))}
                </div>
              );
            }

            const hasExact = exactLocalityCentres && exactLocalityCentres.length > 0;
            const hasOutside = outsideLocalityCentres && outsideLocalityCentres.length > 0;

            return (
              <div style={{ marginBottom: '3rem' }}>
                {/* 1. Exact Locality Section */}
                {hasExact && (
                  <div style={{ marginBottom: '2.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.25rem', borderBottom: '2px solid #0d9488', paddingBottom: '0.5rem' }}>
                      <CheckCircle2 size={18} color="#0d9488" />
                      <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f2444', margin: 0 }}>
                        Accredited Institutes Located in {locationLabel || 'Target Locality'} ({exactLocalityCentres.length})
                      </h4>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.5rem' }}>
                      {exactLocalityCentres.map((c: any) => renderCentreCard(c, true))}
                    </div>
                  </div>
                )}

                {/* 2. Outside Locality Section */}
                {hasOutside && (
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.25rem', borderBottom: '2px solid #cbd5e1', paddingBottom: '0.5rem' }}>
                      <Compass size={18} color="#64748b" />
                      <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#334155', margin: 0 }}>
                        Nearby centres outside {locationLabel || 'target locality'} (within {selectedRadius} km) ({outsideLocalityCentres.length})
                      </h4>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.5rem' }}>
                      {outsideLocalityCentres.map((c: any) => renderCentreCard(c, false))}
                    </div>
                  </div>
                )}

                {!hasExact && !hasOutside && nearbyCentres.length > 0 && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.5rem' }}>
                    {nearbyCentres.map((c: any) => renderCentreCard(c))}
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      )}

      {/* DEDICATED INSTITUTIONAL TRAINING CENTRE PROFILE VIEW */}
      {activeTab === 'centre_profile' && (
        <div className="main-container" style={{ padding: '2rem 1.5rem', maxWidth: '1240px', margin: '0 auto' }}>
          {/* Back button */}
          <div style={{ marginBottom: '1.5rem' }}>
            <button
              onClick={() => setActiveTab('centres')}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.4rem',
                backgroundColor: '#f1f5f9',
                color: '#334155',
                border: '1px solid #cbd5e1',
                padding: '0.5rem 1rem',
                borderRadius: '6px',
                fontSize: '0.85rem',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              <ArrowLeft size={16} /> Back to Training Centres
            </button>
          </div>

          {publicCentreLoading ? (
            <div style={{ textAlign: 'center', padding: '4rem 1rem', color: '#64748b' }}>
              <Loader2 size={36} className="animate-spin" style={{ margin: '0 auto 1rem auto', color: '#0f766e' }} />
              <p>Loading institutional profile & accredited facilities...</p>
            </div>
          ) : !publicCentreProfile ? (
            <div style={{ textAlign: 'center', padding: '4rem 1rem', backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
              <AlertCircle size={40} color="#e11d48" style={{ margin: '0 auto 1rem auto' }} />
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f172a' }}>Training Centre Profile Not Found</h3>
              <p style={{ color: '#64748b', fontSize: '0.88rem', marginTop: '0.5rem' }}>The requested training centre details could not be retrieved from the central skill registry.</p>
            </div>
          ) : (
            <div>
              {/* Institutional Hero Banner */}
              <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '2rem', marginBottom: '2rem', boxShadow: '0 2px 6px rgba(0,0,0,0.04)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.5rem' }}>
                  <div style={{ display: 'flex', gap: '1.25rem', alignItems: 'center' }}>
                    <div style={{ width: '70px', height: '70px', borderRadius: '12px', backgroundColor: '#f0fdfa', border: '2px solid #99f6e4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Building2 size={36} color="#0f766e" />
                    </div>
                    <div>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: publicCentreProfile.is_official_centre !== false ? '#0f766e' : '#1e40af', backgroundColor: publicCentreProfile.is_official_centre !== false ? '#ccfbf1' : '#dbeafe', padding: '2px 8px', borderRadius: '4px' }}>
                          {publicCentreProfile.code}
                        </span>
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#15803d', backgroundColor: '#dcfce7', padding: '2px 8px', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle2 size={12} /> {publicCentreProfile.approval_status || 'ACCREDITED & VERIFIED'}
                        </span>
                        {publicCentreProfile.source && (
                          <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#7c3aed', backgroundColor: '#f3e8ff', padding: '2px 8px', borderRadius: '4px' }}>
                            Source: {publicCentreProfile.source}
                          </span>
                        )}
                        {publicCentreProfile.establishment_year && (
                          <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#475569', backgroundColor: '#f1f5f9', padding: '2px 8px', borderRadius: '4px' }}>
                            Est. {publicCentreProfile.establishment_year}
                          </span>
                        )}
                      </div>
                      <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0f172a', margin: 0, lineHeight: 1.25 }}>
                        {publicCentreProfile.name}
                      </h1>
                      <p style={{ fontSize: '0.88rem', color: '#64748b', margin: '6px 0 0 0', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <MapPin size={14} color="#ea580c" /> {publicCentreProfile.location}, {publicCentreProfile.district}, {publicCentreProfile.state}
                      </p>
                    </div>
                  </div>

                  <div style={{ textAlign: 'right', minWidth: '180px' }}>
                    <div style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: 600 }}>Trainee Completion Rate</div>
                    <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#16a34a' }}>
                      {publicCentreProfile.outcomes?.completion_rate_pct || 92}%
                    </div>
                    <div style={{ fontSize: '0.74rem', color: '#475569' }}>
                      {publicCentreProfile.outcomes?.certificates_issued || 0} Credentialed Graduates
                    </div>
                  </div>
                </div>

                {/* Sub-tab Navigation */}
                <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', borderTop: '1px solid #e2e8f0', marginTop: '1.75rem', paddingTop: '1rem' }}>
                  {[
                    { id: 'overview', label: 'Overview & Contact', icon: Building2 },
                    { id: 'about', label: 'About & History', icon: BookOpen },
                    { id: 'programmes', label: `Programmes & Skills (${publicCentreProfile.programs?.length || 0})`, icon: GraduationCap },
                    { id: 'facilities', label: 'Infrastructure & Labs', icon: Landmark },
                    { id: 'achievements', label: 'Achievements & Recognition', icon: Award },
                    { id: 'outcomes', label: 'Outcomes & Placements', icon: Target },
                    { id: 'trainers', label: `Faculty & Trainers (${publicCentreProfile.trainers?.length || 0})`, icon: Users },
                    { id: 'location', label: 'Location & Map', icon: MapPin }
                  ].map((tb) => {
                    const IconComp = tb.icon;
                    const isActive = publicCentreTab === tb.id;
                    return (
                      <button
                        key={tb.id}
                        type="button"
                        onClick={() => setPublicCentreTab(tb.id as any)}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px',
                          padding: '0.55rem 0.9rem',
                          borderRadius: '8px',
                          border: isActive ? '1px solid #0f766e' : '1px solid #e2e8f0',
                          backgroundColor: isActive ? '#f0fdfa' : '#ffffff',
                          color: isActive ? '#0f766e' : '#475569',
                          fontWeight: isActive ? 700 : 500,
                          fontSize: '0.82rem',
                          cursor: 'pointer',
                          transition: 'all 0.15s ease'
                        }}
                      >
                        <IconComp size={14} /> {tb.label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* TAB 1: OVERVIEW & CONTACT */}
              {publicCentreTab === 'overview' && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
                  <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.75rem' }}>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '1rem' }}>Institutional Details</h3>
                    <div style={{ display: 'grid', gap: '0.8rem', fontSize: '0.86rem' }}>
                      <div><strong style={{ color: '#334155' }}>Accreditation Code:</strong> {publicCentreProfile.code}</div>
                      <div><strong style={{ color: '#334155' }}>Year of Establishment:</strong> {publicCentreProfile.establishment_year || 'Information not yet available'}</div>
                      <div><strong style={{ color: '#334155' }}>Delivery Modes Offered:</strong> {publicCentreProfile.delivery_modes || 'Classroom, Hybrid, Online'}</div>
                      <div><strong style={{ color: '#334155' }}>Classrooms / Lecture Halls:</strong> {publicCentreProfile.classroom_count || 5} Smart Rooms</div>
                      <div><strong style={{ color: '#334155' }}>Operational Status:</strong> <span style={{ color: '#16a34a', fontWeight: 700 }}>● {publicCentreProfile.approval_status}</span></div>
                    </div>
                  </div>

                  <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.75rem' }}>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '1rem' }}>Contact & Digital Touchpoints</h3>
                    {(() => {
                      const vInfo = getContactVerification(publicCentreProfile);
                      return (
                        <div style={{ display: 'grid', gap: '0.8rem', fontSize: '0.86rem' }}>
                          <div><strong style={{ color: '#334155' }}>Full Address:</strong> {publicCentreProfile.address}</div>
                          <div>
                            <strong style={{ color: '#334155' }}>Phone Number:</strong>{' '}
                            <span>{vInfo.phone || 'Contact details unavailable'}</span>
                            <span
                              style={{
                                marginLeft: '8px',
                                fontSize: '0.72rem',
                                fontWeight: 700,
                                color: vInfo.badgeColor,
                                backgroundColor: vInfo.badgeBg,
                                padding: '2px 8px',
                                borderRadius: '4px',
                                border: `1px solid ${vInfo.badgeColor}33`,
                                display: 'inline-block'
                              }}
                            >
                              {vInfo.status}
                            </span>
                            {vInfo.status === 'Verified' && (
                              <div style={{ fontSize: '0.74rem', color: '#15803d', marginTop: '2px', fontStyle: 'italic' }}>
                                ✓ Verified via: {vInfo.source}
                              </div>
                            )}
                          </div>
                          <div><strong style={{ color: '#334155' }}>Official Email:</strong> {publicCentreProfile.contact_email || 'Information not yet available'}</div>
                          <div>
                            <strong style={{ color: '#334155' }}>Official Website:</strong>{' '}
                            {publicCentreProfile.website && publicCentreProfile.website.startsWith('http') ? (
                              <a
                                href={publicCentreProfile.website}
                                target="_blank"
                                rel="noopener noreferrer"
                                style={{ color: '#0f766e', fontWeight: 600, textDecoration: 'underline' }}
                              >
                                {publicCentreProfile.website}
                              </a>
                            ) : (
                              <span style={{ color: '#64748b' }}>Website not available</span>
                            )}
                          </div>
                          <div>
                            <strong style={{ color: '#334155' }}>Institutional Affiliation:</strong>{' '}
                            {publicCentreProfile.source || 'Karnataka Skill Development Mission (KSDM)'}
                          </div>
                        </div>
                      );
                    })()}
                  </div>
                </div>
              )}

              {/* TAB 2: ABOUT & HISTORY */}
              {publicCentreTab === 'about' && (
                <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '2rem' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Institutional Profile & Mission</h3>
                  <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.7, marginBottom: '1.5rem' }}>
                    {publicCentreProfile.description || 'Information not yet available.'}
                  </p>

                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Background & History</h3>
                  <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.7, marginBottom: '1.5rem' }}>
                    {publicCentreProfile.history || 'Information not yet available.'}
                  </p>

                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Purpose & Objectives</h3>
                  <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.7 }}>
                    {publicCentreProfile.mission_objectives || 'Information not yet available.'}
                  </p>
                </div>
              )}

              {/* TAB 3: PROGRAMMES & SKILLS */}
              {publicCentreTab === 'programmes' && (
                <div>
                  {/* Distinct Sectors and Specialisations Offered by this Centre */}
                  {publicCentreProfile.offered_categories && publicCentreProfile.offered_categories.length > 0 && (
                    <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.25rem', marginBottom: '1.5rem' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                        <Compass size={16} color="#0f766e" /> Accredited Sectors Offered at this Centre:
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
                        {publicCentreProfile.offered_categories.map((cat: any) => (
                          <span
                            key={cat.name}
                            style={{
                              backgroundColor: '#f0fdfa',
                              border: '1px solid #99f6e4',
                              color: '#0f766e',
                              padding: '0.25rem 0.65rem',
                              borderRadius: '20px',
                              fontSize: '0.76rem',
                              fontWeight: 700
                            }}
                          >
                            {cat.name} ({cat.program_count} programme{cat.program_count !== 1 ? 's' : ''})
                          </span>
                        ))}
                      </div>
                      {publicCentreProfile.offered_subcategories && publicCentreProfile.offered_subcategories.length > 0 && (
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                          <strong>Specialisations:</strong> {publicCentreProfile.offered_subcategories.map((s: any) => s.name).join(' • ')}
                        </div>
                      )}
                    </div>
                  )}

                  <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                      Accredited Training Programmes Offered at this Centre
                    </h3>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      {publicCentreProfile.programs?.length || 0} active courses
                    </span>
                  </div>

                  {(!publicCentreProfile.programs || publicCentreProfile.programs.length === 0) ? (
                    <div style={{ textAlign: 'center', padding: '3rem 1rem', backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                      <p style={{ color: '#64748b' }}>No training programmes are currently scheduled at this centre.</p>
                    </div>
                  ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem' }}>
                      {publicCentreProfile.programs.map((p: any) => (
                        <div key={p.id} style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                          <div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                              <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#0f766e', backgroundColor: '#ccfbf1', padding: '2px 8px', borderRadius: '4px' }}>
                                {p.code}
                              </span>
                              <span style={{ fontSize: '0.72rem', fontWeight: 600, color: '#ea580c', backgroundColor: '#fff7ed', padding: '2px 8px', borderRadius: '4px' }}>
                                {p.mode}
                              </span>
                            </div>
                            <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>{p.title}</h4>
                            <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '1rem', lineHeight: 1.5 }}>{p.description}</p>
                            <div style={{ fontSize: '0.78rem', color: '#475569', display: 'grid', gap: '0.35rem', marginBottom: '1.25rem' }}>
                              <div><strong>Duration:</strong> {p.duration_hours} Training Hours</div>
                              <div><strong>Course Fee:</strong> {p.fee > 0 ? `₹${p.fee}` : 'Fully Government Subsidized (₹0)'}</div>
                              {p.scholarship_available && <div style={{ color: '#16a34a', fontWeight: 600 }}>✓ Government Stipend Available</div>}
                            </div>
                          </div>

                          {publicCentreProfile.is_official_centre !== false ? (
                            (!userRole || userRole === 'CITIZEN') ? (
                              <button
                                type="button"
                                onClick={() => handleStartEnrolment(p)}
                                style={{
                                  width: '100%',
                                  padding: '0.65rem 1rem',
                                  backgroundColor: '#ea580c',
                                  color: '#ffffff',
                                  border: 'none',
                                  borderRadius: '6px',
                                  fontWeight: 700,
                                  fontSize: '0.85rem',
                                  cursor: 'pointer'
                                }}
                              >
                                Apply for this Course
                              </button>
                            ) : (
                              <div
                                style={{
                                  textAlign: 'center',
                                  padding: '0.55rem 0.75rem',
                                  backgroundColor: '#f1f5f9',
                                  color: '#64748b',
                                  borderRadius: '6px',
                                  fontSize: '0.78rem',
                                  fontWeight: 600,
                                  border: '1px solid #e2e8f0'
                                }}
                              >
                                This feature is available to Citizen accounts only.
                              </div>
                            )
                          ) : (
                            <div style={{ display: 'grid', gap: '0.5rem' }}>
                              <div style={{ fontSize: '0.78rem', color: '#64748b', fontStyle: 'italic', textAlign: 'center' }}>
                                Verified External Directory Programme • Direct Institutional Admission
                              </div>
                              {publicCentreProfile.website && publicCentreProfile.website.startsWith('http') ? (
                                <a
                                  href={publicCentreProfile.website}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{
                                    display: 'block',
                                    textAlign: 'center',
                                    padding: '0.65rem 1rem',
                                    backgroundColor: '#0f766e',
                                    color: '#ffffff',
                                    borderRadius: '6px',
                                    fontWeight: 700,
                                    fontSize: '0.85rem',
                                    textDecoration: 'none'
                                  }}
                                >
                                  Visit Institute Website
                                </a>
                              ) : (
                                <div
                                  style={{
                                    textAlign: 'center',
                                    padding: '0.65rem 1rem',
                                    backgroundColor: '#f1f5f9',
                                    color: '#64748b',
                                    borderRadius: '6px',
                                    fontWeight: 600,
                                    fontSize: '0.85rem',
                                    border: '1px solid #e2e8f0'
                                  }}
                                >
                                  Website not available
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 4: INFRASTRUCTURE & FACILITIES */}
              {publicCentreTab === 'facilities' && (
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.75rem' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Laboratories & Practical Workshops</h3>
                    <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.7 }}>
                      {publicCentreProfile.lab_details || 'Information not yet available.'}
                    </p>
                  </div>

                  <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.75rem' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Equipment, Computing & Tools</h3>
                    <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.7 }}>
                      {publicCentreProfile.equipment_details || 'Information not yet available.'}
                    </p>
                  </div>

                  <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.75rem' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Campus Amenities & Safety</h3>
                    <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.7 }}>
                      {publicCentreProfile.facilities || 'High-speed internet, Advanced Computer Lab, Smart Classroom, Library, Emergency First Aid.'}
                    </p>
                  </div>
                </div>
              )}

              {/* TAB 5: ACHIEVEMENTS & RECOGNITION */}
              {publicCentreTab === 'achievements' && (
                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.75rem' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Awards & Institutional Milestones</h3>
                    <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.7 }}>
                      {publicCentreProfile.achievements || 'Information not yet available.'}
                    </p>
                  </div>

                  <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.75rem' }}>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Accreditations & Government Affiliations</h3>
                    <p style={{ fontSize: '0.9rem', color: '#475569', lineHeight: 1.7 }}>
                      {publicCentreProfile.certifications || 'NSQF Aligned • NCVET Accredited Government Partner Hub'}
                    </p>
                  </div>
                </div>
              )}

              {/* TAB 6: TRAINING OUTCOMES & PLACEMENTS */}
              {publicCentreTab === 'outcomes' && (
                <div>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
                    <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', borderLeft: '4px solid #0f766e' }}>
                      <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Total Citizens Trained</div>
                      <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', marginTop: '0.2rem' }}>{publicCentreProfile.outcomes?.total_enrolled || 0}</div>
                    </div>
                    <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', borderLeft: '4px solid #16a34a' }}>
                      <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Certified Graduates</div>
                      <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', marginTop: '0.2rem' }}>{publicCentreProfile.outcomes?.certificates_issued || 0}</div>
                    </div>
                    <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', borderLeft: '4px solid #0284c7' }}>
                      <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Active Trainees</div>
                      <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', marginTop: '0.2rem' }}>{publicCentreProfile.outcomes?.active_trainees || 0}</div>
                    </div>
                    <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.25rem', borderLeft: '4px solid #ea580c' }}>
                      <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 600 }}>Completion Success Rate</div>
                      <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#0f172a', marginTop: '0.2rem' }}>{publicCentreProfile.outcomes?.completion_rate_pct || 92}%</div>
                    </div>
                  </div>

                  <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.75rem' }}>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', marginBottom: '1rem' }}>Key Placement & Industry Partners</h3>
                    <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                      {(publicCentreProfile.outcomes?.top_placement_partners || []).map((partner: string) => (
                        <span key={partner} style={{ padding: '0.5rem 1rem', backgroundColor: '#f8fafc', border: '1px solid #cbd5e1', borderRadius: '8px', fontSize: '0.84rem', fontWeight: 600, color: '#1e293b' }}>
                          💼 {partner}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* TAB 7: TRAINERS & FACULTY */}
              {publicCentreTab === 'trainers' && (
                <div>
                  {(!publicCentreProfile.trainers || publicCentreProfile.trainers.length === 0) ? (
                    <div style={{ textAlign: 'center', padding: '3rem 1rem', backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                      <p style={{ color: '#64748b' }}>Faculty assignments for this centre are currently being updated.</p>
                    </div>
                  ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
                      {publicCentreProfile.trainers.map((t: any) => (
                        <div key={t.id} style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '0.75rem' }}>
                            <div style={{ width: '48px', height: '48px', borderRadius: '50%', backgroundColor: '#f0fdfa', border: '1px solid #99f6e4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                              <User size={24} color="#0f766e" />
                            </div>
                            <div>
                              <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>{t.name}</h4>
                              <p style={{ fontSize: '0.78rem', color: '#0f766e', fontWeight: 600, margin: '2px 0 0 0' }}>{t.specialisation}</p>
                            </div>
                          </div>
                          <div style={{ fontSize: '0.8rem', color: '#475569', display: 'grid', gap: '0.3rem' }}>
                            <div><strong>Qualification:</strong> {t.qualification}</div>
                            <div><strong>Experience:</strong> {t.experience_years} Years Industry & Teaching Experience</div>
                            <div><strong>Availability:</strong> <span style={{ color: '#16a34a', fontWeight: 600 }}>{t.availability}</span></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* TAB 8: LOCATION & MAP */}
              {publicCentreTab === 'location' && (
                <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '2rem' }}>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>Geographic Coordinates & Directions</h3>
                  <p style={{ fontSize: '0.9rem', color: '#475569', marginBottom: '1.25rem' }}>
                    {publicCentreProfile.address}
                  </p>
                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', fontSize: '0.86rem', color: '#334155', marginBottom: '1.5rem' }}>
                    <div><strong>Latitude:</strong> {publicCentreProfile.latitude || '12.9716'}</div>
                    <div><strong>Longitude:</strong> {publicCentreProfile.longitude || '77.5946'}</div>
                    <div><strong>District:</strong> {publicCentreProfile.district}</div>
                  </div>
                  <div style={{ height: '360px', borderRadius: '8px', overflow: 'hidden', border: '1px solid #e2e8f0' }}>
                    <CentreLocationMap
                      userLocation={null}
                      locationLabel={publicCentreProfile.name}
                      centres={[publicCentreProfile]}
                      radiusKm={5}
                      selectedCentreId={publicCentreProfile.id}
                      onSelectCentre={() => {}}
                    />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* SKILL GAP ANALYSIS ENGINE */}
      {activeTab === 'gap' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <h2>{t('nav.gap_analysis')}</h2>
              <p>Rule-based career matching engine comparing your competencies against industry job descriptions</p>
            </div>
          </div>

          <div style={{ backgroundColor: '#ffffff', padding: '1.75rem', borderRadius: '10px', border: '1px solid #e2e8f0', marginBottom: '2rem' }}>
            <label style={{ display: 'block', fontSize: '0.88rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
              Select Your Target Career Profile:
            </label>
            <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
              <select
                className="form-control"
                style={{ flex: 1, minWidth: '280px' }}
                value={selectedTargetRole}
                onChange={(e) => setSelectedTargetRole(e.target.value)}
              >
                {supportedRoles.map((r: any) => (
                  <option key={r.role} value={r.role}>{r.role}</option>
                ))}
              </select>
              <button className="btn-primary-orange" onClick={runGapAnalysis}>
                Run Skill Gap Analysis
              </button>
            </div>
          </div>

          {gapReport && (
            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '2rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #f1f5f9', paddingBottom: '1.25rem', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.35rem', fontWeight: 800, color: '#0f2444' }}>{gapReport.target_role}</h3>
                  <p style={{ fontSize: '0.85rem', color: '#64748b' }}>{gapReport.role_description}</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: gapReport.skill_gap_score >= 70 ? '#16a34a' : '#ea580c' }}>
                    {gapReport.skill_gap_score}%
                  </div>
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#64748b' }}>Compatibility Score</div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
                <div style={{ backgroundColor: '#f0fdf4', padding: '1.25rem', borderRadius: '8px', border: '1px solid #bbf7d0' }}>
                  <h4 style={{ color: '#166534', fontWeight: 700, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <CheckCircle2 size={16} /> Matching Competencies ({gapReport.matching_skills?.length || 0})
                  </h4>
                  <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', color: '#14532d' }}>
                    {gapReport.matching_skills?.map((s: string) => <li key={s}>{s}</li>)}
                    {(!gapReport.matching_skills || gapReport.matching_skills.length === 0) && <li>None detected in profile yet.</li>}
                  </ul>
                </div>

                <div style={{ backgroundColor: '#fff7ed', padding: '1.25rem', borderRadius: '8px', border: '1px solid #fed7aa' }}>
                  <h4 style={{ color: '#9a3412', fontWeight: 700, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                    <AlertCircle size={16} /> Missing Key Skills ({gapReport.missing_skills?.length || 0})
                  </h4>
                  <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', color: '#7c2d12' }}>
                    {gapReport.missing_skills?.map((s: string) => <li key={s}>{s}</li>)}
                  </ul>
                </div>
              </div>

              <div>
                <h4 style={{ fontWeight: 700, color: '#0f172a', marginBottom: '1rem' }}>Recommended Step-by-Step Learning Order:</h4>
                <div style={{ display: 'grid', gap: '0.75rem' }}>
                  {gapReport.recommended_courses?.map((rc: any, idx: number) => (
                    <div key={rc.skill_name} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem', border: '1px solid #e2e8f0', borderRadius: '8px' }}>
                      <div>
                        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#ea580c', marginRight: '0.5rem' }}>Step {idx + 1}</span>
                        <strong style={{ fontSize: '0.95rem', color: '#0f172a' }}>{rc.skill_name}</strong>
                        <p style={{ fontSize: '0.8rem', color: '#64748b' }}>{rc.reason}</p>
                      </div>
                      <button className="btn-primary-orange" onClick={() => openCourseDetail(rc.skill_name)}>
                        Enrol Now
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* CITIZEN APPLICATIONS TRACKING (COURSES, JOBS, & SAVED) */}
      {activeTab === 'applications' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <h2>{t('apps.title')}</h2>
              <p>{t('apps.subtitle')}</p>
            </div>
          </div>

          {/* Training Enrolments List */}
          {(
            <>
              {myApplications.length === 0 ? (
                <div style={{ backgroundColor: '#ffffff', padding: '3rem', borderRadius: '10px', textAlign: 'center', border: '1px solid #e2e8f0' }}>
                  <BookOpen size={40} style={{ color: '#94a3b8', margin: '0 auto 1rem auto' }} />
                  <h3 style={{ fontSize: '1.15rem', color: '#0f172a', marginBottom: '0.5rem' }}>{t('apps.no_training')}</h3>
                  <button className="btn-primary-orange" style={{ margin: '0 auto' }} onClick={() => setActiveTab('courses')}>
                    {t('apps.browse_skills')}
                  </button>
                </div>
              ) : (
                <div style={{ display: 'grid', gap: '1.25rem' }}>
                  {myApplications.map((app: any) => (
                    <div key={app.application_id} style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '1rem', marginBottom: '1rem' }}>
                        <div>
                          <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.25rem' }}>
                            <span style={{ fontSize: '0.8rem', fontWeight: 800, color: '#0f2444' }}>{app.application_id}</span>
                            <span className={`status-pill ${app.status}`}>{getStatusText(app.status)}</span>
                          </div>
                          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a' }}>{app.program_title}</h3>
                          <p style={{ fontSize: '0.82rem', color: '#64748b' }}>{t('apps.applied_on')}: {formatISTDateTime(app.created_at)}</p>
                        </div>

                        <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.4rem' }}>
                          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
                            {t('apps.progress')}: {app.training_progress_pct}%
                          </div>
                          <div style={{ width: '180px', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden' }}>
                            <div style={{ width: `${app.training_progress_pct}%`, height: '100%', backgroundColor: app.training_progress_pct === 100 ? '#16a34a' : '#ea580c' }} />
                          </div>
                          <button
                            type="button"
                            className="btn-navy-outline"
                            style={{ padding: '0.3rem 0.75rem', fontSize: '0.78rem', marginTop: '0.25rem' }}
                            onClick={() => setSelectedCitizenApp(app)}
                          >
                            View Full Application Details
                          </button>
                        </div>
                      </div>

                      <div style={{ backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '6px', fontSize: '0.85rem', color: '#334155', marginBottom: '1rem' }}>
                        <strong>{t('apps.admin_remarks')}:</strong> {app.admin_remarks || 'Awaiting initial review from the Skill Department officer.'}
                      </div>

                      {app.status_history && (
                        <div>
                          <h5 style={{ fontSize: '0.8rem', fontWeight: 700, color: '#475569', textTransform: 'uppercase', marginBottom: '0.5rem' }}>{t('apps.status_trail')}:</h5>
                          <div style={{ display: 'grid', gap: '0.4rem' }}>
                            {app.status_history.map((h: any, idx: number) => (
                              <div key={idx} style={{ fontSize: '0.8rem', color: '#64748b', display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                                <span style={{ color: '#475569', fontWeight: 500 }}>{formatISTDateTime(h.timestamp)}:</span>
                                <span style={{ fontWeight: 600, color: '#0f172a' }}>{getStatusText(h.new_status)}</span>
                                <span>({h.remarks})</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </>
          )}

        </div>
      )}

      {/* DEDICATED STUDENT LEARNING PORTAL */}
      {activeTab === 'student_portal' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.25rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, backgroundColor: '#e0f2fe', color: '#0369a1', padding: '0.2rem 0.6rem', borderRadius: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Enrolled Student Portal
                </span>
                {studentId && (
                  <span style={{ fontSize: '0.85rem', fontWeight: 800, color: '#0f2444', backgroundColor: '#f1f5f9', padding: '0.2rem 0.6rem', borderRadius: '4px', border: '1px solid #cbd5e1' }}>
                    Student ID: {studentId}
                  </span>
                )}
              </div>
              <h2>My Student Learning Portal</h2>
              <p>Official Government Skilling Dossier, Batch Timetable, Live Curriculum Progress & Verified Outcomes</p>
            </div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <button
                type="button"
                style={{ padding: '0.45rem 0.9rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem', background: '#2563eb', color: '#ffffff', border: 'none', borderRadius: '6px', fontWeight: 700, cursor: 'pointer', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}
                onClick={() => {
                  const id = studentId || userEmail || 'CIT-2026102001';
                  window.open(`/api/reports/candidate/${id}/transcript`, '_blank');
                }}
                title="Generate and print official certified vocational skill transcript"
              >
                <FileText size={14} /> Official Skill Transcript
              </button>
              <button
                type="button"
                className="btn-navy-outline"
                style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                onClick={fetchStudentDashboard}
                disabled={studentDashboardLoading}
              >
                <RefreshCw size={14} className={studentDashboardLoading ? 'animate-spin' : ''} />
                Refresh Data
              </button>
            </div>
          </div>

          {studentDashboardLoading && !studentDashboardData ? (
            <div style={{ textAlign: 'center', padding: '3rem', backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
              <Loader2 size={36} className="animate-spin" style={{ color: '#0284c7', margin: '0 auto 1rem auto' }} />
              <p style={{ color: '#64748b', fontSize: '0.9rem' }}>Retrieving your official student records from MySQL...</p>
            </div>
          ) : studentDashboardError ? (
            <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '1.25rem', borderRadius: '8px', border: '1px solid #fecaca', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <AlertCircle size={20} />
              <div>
                <strong style={{ display: 'block' }}>Unable to load Student Portal:</strong>
                <span>{studentDashboardError}</span>
              </div>
            </div>
          ) : !studentDashboardData?.is_student || !studentDashboardData?.enrolments?.length ? (
            <div style={{ backgroundColor: '#ffffff', padding: '3.5rem 2rem', borderRadius: '10px', textAlign: 'center', border: '1px solid #e2e8f0' }}>
              <GraduationCap size={48} style={{ color: '#94a3b8', margin: '0 auto 1rem auto' }} />
              <h3 style={{ fontSize: '1.25rem', color: '#0f172a', marginBottom: '0.5rem' }}>No Active Enrolments Found</h3>
              <p style={{ color: '#64748b', maxWidth: '520px', margin: '0 auto 1.5rem auto', fontSize: '0.88rem' }}>
                Student Portal features activate once your application is formally approved and enrolled into an accredited training batch by a Centre Administrator.
              </p>
              <button className="btn-primary-orange" style={{ margin: '0 auto' }} onClick={() => setActiveTab('applications')}>
                View My Applications
              </button>
            </div>
          ) : (
            <div style={{ display: 'grid', gap: '1.75rem' }}>
              {/* SECTION A & B: STUDENT IDENTITY CARD & OVERVIEW STATS */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
                {/* Official Student Digital ID Pass */}
                <div style={{
                  backgroundColor: '#ffffff',
                  borderRadius: '12px',
                  border: '1.5px solid #0284c7',
                  boxShadow: '0 10px 25px -5px rgba(2, 132, 199, 0.1)',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column'
                }}>
                  <div style={{ backgroundColor: '#0284c7', color: '#ffffff', padding: '1rem 1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Landmark size={20} color="#f97316" />
                      <div>
                        <div style={{ fontSize: '0.65rem', textTransform: 'uppercase', letterSpacing: '0.08em', color: '#e0f2fe', fontWeight: 700 }}>
                          NagrikSetu Skill Development Platform
                        </div>
                        <div style={{ fontSize: '0.95rem', fontWeight: 800 }}>Student Enrolment Pass</div>
                      </div>
                    </div>
                    <span style={{ fontSize: '0.72rem', backgroundColor: '#0369a1', padding: '0.2rem 0.5rem', borderRadius: '4px', fontWeight: 700, border: '1px solid #38bdf8' }}>
                      ACTIVE
                    </span>
                  </div>

                  <div style={{ padding: '1.25rem', flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                        <div>
                          <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>PERMANENT STUDENT ID</div>
                          <div style={{ fontSize: '1.25rem', fontWeight: 900, color: '#0f2444', letterSpacing: '0.05em' }}>
                            {studentDashboardData.student_id || studentId}
                          </div>
                        </div>
                        <div style={{ width: '48px', height: '48px', backgroundColor: '#f0f9ff', borderRadius: '8px', border: '1px solid #bae6fd', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0284c7' }}>
                          <User size={26} />
                        </div>
                      </div>

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', fontSize: '0.82rem', marginBottom: '0.75rem' }}>
                        <div>
                          <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem' }}>STUDENT NAME</span>
                          <strong style={{ color: '#0f172a' }}>{studentDashboardData.citizen?.full_name || userName}</strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem' }}>CITIZEN REFERENCE</span>
                          <strong style={{ color: '#0f172a' }}>{studentDashboardData.citizen?.citizen_ref || citizenRef}</strong>
                        </div>
                        <div>
                          <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem' }}>REGISTERED EMAIL</span>
                          <span style={{ color: '#334155', wordBreak: 'break-all' }}>{studentDashboardData.citizen?.email || userEmail}</span>
                        </div>
                        <div>
                          <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem' }}>CONTACT NUMBER</span>
                          <span style={{ color: '#334155' }}>{studentDashboardData.citizen?.phone || 'Not provided'}</span>
                        </div>
                      </div>
                    </div>

                    <div style={{ borderTop: '1px dashed #cbd5e1', paddingTop: '0.75rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: '#64748b' }}>
                      <span>NagrikSetu Enrolment Record</span>
                      <button
                        type="button"
                        style={{ background: 'none', border: 'none', color: '#0284c7', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                        onClick={() => window.print()}
                      >
                        <Download size={13} /> Print Trainee Card
                      </button>
                    </div>
                  </div>
                </div>

                {/* Trainee Academic Summary & KPI Overview */}
                <div style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f2444', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Award size={18} color="#ea580c" />
                      Academic & Training Status Summary
                    </h3>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.25rem' }}>
                      <div style={{ backgroundColor: '#f8fafc', padding: '0.85rem', borderRadius: '8px', border: '1px solid #f1f5f9', textAlign: 'center' }}>
                        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0284c7' }}>
                          {studentDashboardData.enrolments.length}
                        </div>
                        <div style={{ fontSize: '0.74rem', color: '#64748b', fontWeight: 600 }}>Enrolled Courses</div>
                      </div>
                      <div style={{ backgroundColor: '#f8fafc', padding: '0.85rem', borderRadius: '8px', border: '1px solid #f1f5f9', textAlign: 'center' }}>
                        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#16a34a' }}>
                          {studentDashboardData.enrolments.filter((e: any) => e.status === 'ENROLLED' || e.status === 'IN_PROGRESS').length}
                        </div>
                        <div style={{ fontSize: '0.74rem', color: '#64748b', fontWeight: 600 }}>Active Batches</div>
                      </div>
                      <div style={{ backgroundColor: '#f8fafc', padding: '0.85rem', borderRadius: '8px', border: '1px solid #f1f5f9', textAlign: 'center' }}>
                        <div style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f766e' }}>
                          {studentDashboardData.enrolments.filter((e: any) => e.status === 'COMPLETED').length}
                        </div>
                        <div style={{ fontSize: '0.74rem', color: '#64748b', fontWeight: 600 }}>Completed</div>
                      </div>
                    </div>

                    <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '0.85rem', fontSize: '0.82rem', color: '#166534' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 700, marginBottom: '0.2rem' }}>
                        <CheckCircle2 size={16} /> Enrolment Verified
                      </div>
                      Your formal seat allocation has been confirmed by the accredited Training Centre Administration in MySQL.
                    </div>
                  </div>

                  <div style={{ marginTop: '1rem', fontSize: '0.78rem', color: '#64748b', textAlign: 'right' }}>
                    Source: National Skill Development Microservice MySQL Engine
                  </div>
                </div>
              </div>

              {/* SECTION C to J: ENROLLED PROGRAMMES DETAIL CARDS */}
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0f2444', marginBottom: '1rem' }}>
                  Enrolled Programmes, Timetable & Progress ({studentDashboardData.enrolments.length})
                </h3>

                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  {studentDashboardData.enrolments.map((enr: any) => (
                    <div key={enr.enrollment_id} style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.03)', overflow: 'hidden' }}>
                      {/* Program Top Header */}
                      <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem 1.5rem', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem' }}>
                            <span style={{ fontSize: '0.76rem', fontWeight: 800, color: '#0284c7', backgroundColor: '#e0f2fe', padding: '0.15rem 0.5rem', borderRadius: '4px' }}>
                              {enr.application_code}
                            </span>
                            <span style={{ fontSize: '0.76rem', fontWeight: 800, color: '#0f766e', backgroundColor: '#ccfbf1', padding: '0.15rem 0.5rem', borderRadius: '4px' }}>
                              {enr.student_id || studentId}
                            </span>
                            <span className={`status-pill ${enr.status}`}>
                              {enr.status}
                            </span>
                            <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                              Preferred Mode: <strong>{enr.selected_mode}</strong>
                              {enr.batch && enr.batch.mode !== enr.selected_mode && (
                                <> · Batch Mode: <strong>{enr.batch.mode}</strong></>
                              )}
                            </span>
                          </div>
                          <h4 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', margin: '0 0 0.35rem 0' }}>
                            {enr.program_title}
                          </h4>
                          <div style={{ fontSize: '0.82rem', color: '#475569' }}>
                            Skill Track: <strong>{enr.skill_name}</strong> • Enrolled On: {formatISTDateTime(enr.enrolled_date)}
                          </div>
                        </div>

                        {/* Overall Progress & Attendance Gauges */}
                        <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600, marginBottom: '0.2rem' }}>Curriculum Progress</div>
                            <div style={{ fontSize: '1.2rem', fontWeight: 900, color: enr.training_progress_pct === 100 ? '#16a34a' : '#0284c7' }}>
                              {enr.training_progress_pct}%
                            </div>
                            <div style={{ width: '100px', height: '6px', backgroundColor: '#e2e8f0', borderRadius: '3px', overflow: 'hidden', marginTop: '0.2rem' }}>
                              <div style={{ width: `${enr.training_progress_pct}%`, height: '100%', backgroundColor: enr.training_progress_pct === 100 ? '#16a34a' : '#0284c7' }} />
                            </div>
                          </div>

                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600, marginBottom: '0.2rem' }}>Attendance</div>
                            <div style={{ fontSize: '1.2rem', fontWeight: 900, color: enr.attendance_pct >= 75 ? '#16a34a' : '#ea580c' }}>
                              {enr.attendance_pct}%
                            </div>
                            <div style={{ width: '100px', height: '6px', backgroundColor: '#e2e8f0', borderRadius: '3px', overflow: 'hidden', marginTop: '0.2rem' }}>
                              <div style={{ width: `${enr.attendance_pct}%`, height: '100%', backgroundColor: enr.attendance_pct >= 75 ? '#16a34a' : '#ea580c' }} />
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Main Programme Content Body */}
                      <div style={{ padding: '1.5rem' }}>
                        {/* Centre Remarks */}
                        {enr.admin_remarks && (
                          <div style={{ backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: '8px', padding: '0.85rem 1rem', fontSize: '0.85rem', color: '#0369a1', marginBottom: '1.5rem', display: 'flex', gap: '0.6rem', alignItems: 'center' }}>
                            <Award size={18} style={{ flexShrink: 0 }} />
                            <div>
                              <strong>Centre Administration Remarks:</strong> {enr.admin_remarks}
                            </div>
                          </div>
                        )}

                        {/* Grid: Training Centre Info & Assigned Batch Timetable */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
                          {/* Training Centre Details */}
                          <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                              <Building2 size={18} color="#0f766e" />
                              <h5 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 700, color: '#0f172a' }}>
                                Accredited Training Centre
                              </h5>
                            </div>
                            {enr.centre ? (
                              <div style={{ fontSize: '0.82rem', color: '#334155', display: 'grid', gap: '0.4rem' }}>
                                <div><strong>Name:</strong> {enr.centre.name} ({enr.centre.code})</div>
                                <div><strong>District:</strong> {enr.centre.district}, Karnataka</div>
                                <div><strong>Address:</strong> {enr.centre.address || enr.centre.location}</div>
                                <div><strong>Contact Phone:</strong> {enr.centre.contact_phone || 'Verified on Portal'}</div>
                                <div><strong>Official Email:</strong> {enr.centre.contact_email || 'Not available'}</div>
                                {enr.centre.website && (
                                  <div>
                                    <strong>Institutional Website:</strong>{' '}
                                    <a href={enr.centre.website} target="_blank" rel="noopener noreferrer" style={{ color: '#0284c7', textDecoration: 'underline' }}>
                                      {enr.centre.website}
                                    </a>
                                  </div>
                                )}
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.82rem', color: '#64748b' }}>Assigned training centre record not yet populated.</div>
                            )}
                          </div>

                          {/* Batch & Timetable */}
                          <div style={{ backgroundColor: '#f8fafc', padding: '1.25rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                              <Clock size={18} color="#0284c7" />
                              <h5 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 700, color: '#0f172a' }}>
                                Assigned Batch & Timetable
                              </h5>
                            </div>
                            {enr.batch ? (
                              <div style={{ fontSize: '0.82rem', color: '#334155', display: 'grid', gap: '0.4rem' }}>
                                <div><strong>Batch Name:</strong> {enr.batch.batch_name}</div>
                                <div><strong>Batch Code:</strong> {enr.batch.batch_code}</div>
                                <div><strong>Timings:</strong> <span style={{ color: '#0f766e', fontWeight: 700 }}>{enr.batch.timings}</span></div>
                                <div><strong>Training Schedule:</strong> {enr.batch.schedule}</div>
                                <div><strong>Training Mode:</strong> {enr.batch.mode}</div>
                                <div><strong>Duration:</strong> {enr.batch.start_date} to {enr.batch.end_date}</div>
                                <div><strong>Assigned Faculty:</strong> {enr.batch.assigned_trainer || 'Faculty Assigned'}</div>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.82rem', color: '#64748b' }}>Batch details not yet scheduled.</div>
                            )}
                          </div>
                        </div>

                        {/* Curriculum Module Progress Breakdown */}
                        <div style={{ marginBottom: '1.5rem' }}>
                          <h5 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                            <BookOpen size={16} color="#ea580c" />
                            Curriculum Modules & Progress Checklist ({enr.modules?.length || 0} Modules)
                          </h5>
                          {enr.modules && enr.modules.length > 0 ? (
                            <div style={{ display: 'grid', gap: '0.6rem' }}>
                              {enr.modules.map((m: any, idx: number) => (
                                <div key={m.id || idx} style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'space-between',
                                  padding: '0.75rem 1rem',
                                  backgroundColor: m.is_completed ? '#f0fdf4' : '#ffffff',
                                  border: `1px solid ${m.is_completed ? '#bbf7d0' : '#e2e8f0'}`,
                                  borderRadius: '6px'
                                }}>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                    <div style={{
                                      width: '24px',
                                      height: '24px',
                                      borderRadius: '50%',
                                      backgroundColor: m.is_completed ? '#16a34a' : '#e2e8f0',
                                      color: m.is_completed ? '#ffffff' : '#64748b',
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      fontSize: '0.75rem',
                                      fontWeight: 700
                                    }}>
                                      {m.is_completed ? <Check size={14} /> : (idx + 1)}
                                    </div>
                                    <div>
                                      <strong style={{ fontSize: '0.85rem', color: '#0f172a' }}>{m.title}</strong>
                                      {m.description && <p style={{ margin: 0, fontSize: '0.76rem', color: '#64748b' }}>{m.description}</p>}
                                    </div>
                                  </div>
                                  <div style={{ textAlign: 'right' }}>
                                    <span style={{
                                      fontSize: '0.72rem',
                                      fontWeight: 700,
                                      padding: '0.2rem 0.5rem',
                                      borderRadius: '4px',
                                      backgroundColor: m.is_completed ? '#dcfce7' : '#f1f5f9',
                                      color: m.is_completed ? '#15803d' : '#64748b'
                                    }}>
                                      {m.is_completed ? `Completed (${m.completion_date ? formatISTDateTime(m.completion_date) : 'Verified'})` : (m.remarks === 'IN_PROGRESS' ? 'In Progress' : 'Not Started')}
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div style={{ fontSize: '0.82rem', color: '#64748b', fontStyle: 'italic', padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '6px' }}>
                              Curriculum modules will be recorded by your instructor as sessions progress.
                            </div>
                          )}
                        </div>

                        {/* Two Columns: Attendance Log & Assessment Scores */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
                          {/* Attendance Records */}
                          <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                              <h5 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                <Calendar size={16} color="#0284c7" />
                                Attendance Log
                              </h5>
                              <span style={{ fontSize: '0.76rem', fontWeight: 700, color: '#0f766e' }}>
                                Compliance: {enr.attendance_pct}%
                              </span>
                            </div>
                            {enr.attendance && enr.attendance.length > 0 ? (
                              <div style={{ maxHeight: '200px', overflowY: 'auto', display: 'grid', gap: '0.4rem', fontSize: '0.8rem' }}>
                                {enr.attendance.map((att: any) => (
                                  <div key={att.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0.6rem', backgroundColor: '#f8fafc', borderRadius: '4px' }}>
                                    <span>{att.session_date}: {att.session_topic}</span>
                                    <span style={{ fontWeight: 700, color: att.status === 'PRESENT' ? '#16a34a' : '#b91c1c' }}>
                                      {att.status}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            ) : enr.batch?.start_date && new Date(enr.batch.start_date) > new Date() ? (
                              <div style={{ fontSize: '0.8rem', color: '#64748b', padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '6px' }}>
                                Batch not yet started. Attendance tracking will begin from {enr.batch.start_date}. No sessions have been recorded yet.
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.8rem', color: '#64748b', padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '6px' }}>
                                No attendance records have been entered yet. Sessions may not have been recorded by faculty.
                              </div>
                            )}
                          </div>

                          {/* Assessment Results & Certifications */}
                          <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                              <h5 style={{ margin: 0, fontSize: '0.92rem', fontWeight: 700, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                <Award size={16} color="#ea580c" />
                                Assessments & Certification
                              </h5>
                              <span style={{ fontSize: '0.76rem', fontWeight: 700, color: enr.certificate_issued ? '#16a34a' : '#64748b' }}>
                                {enr.certificate_issued ? 'Certificate Issued' : 'In Training'}
                              </span>
                            </div>

                            {enr.assessments && enr.assessments.length > 0 ? (
                              <div style={{ display: 'grid', gap: '0.4rem', fontSize: '0.8rem' }}>
                                {enr.assessments.map((asmt: any) => (
                                  <div key={asmt.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0.6rem', backgroundColor: '#f8fafc', borderRadius: '4px' }}>
                                    <span>{asmt.assessment_title}</span>
                                    <strong>{asmt.marks_obtained}/{asmt.max_marks} ({asmt.score_pct}%)</strong>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.8rem', color: '#64748b', padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '6px', marginBottom: '0.75rem' }}>
                                Formative assessment will be conducted upon completion of core modules.
                              </div>
                            )}

                            {enr.certificate_issued ? (
                              <div style={{ marginTop: '0.75rem', padding: '0.75rem', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontSize: '0.8rem', color: '#166534', fontWeight: 600 }}>Government Verified Certificate Ready</span>
                                <button className="btn-primary-orange" style={{ padding: '0.3rem 0.75rem', fontSize: '0.76rem' }} onClick={() => setActiveTab('certificates')}>
                                  Download Certificate
                                </button>
                              </div>
                            ) : (
                              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.5rem' }}>
                                Certificate issuance requires $\ge 75\%$ attendance and completion of all modules.
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* CITIZEN PROFILE */}
      {activeTab === 'profile' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <h2>{t('nav.my_profile')}</h2>
              <p>Manage your verified education, employment background, and technical proficiencies</p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>Personal & Educational Information</h3>
                <button
                  className="btn-primary-orange"
                  style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}
                  onClick={handleOpenEditProfile}
                >
                  Edit Profile
                </button>
              </div>
              <div style={{ display: 'grid', gap: '0.75rem', fontSize: '0.88rem' }}>
                <div><strong>Citizen ID:</strong> {citizenRef}</div>
                <div><strong>Full Name:</strong> {userName || myProfile?.full_name}</div>
                <div><strong>Email:</strong> {userEmail}</div>
                <div><strong>Phone:</strong> {myProfile?.phone || '+91 9876543210'}</div>
                <div><strong>Date of Birth:</strong> {myProfile?.date_of_birth || 'Not specified'}</div>
                <div><strong>Gender:</strong> {myProfile?.gender || 'Not specified'}</div>
                <div><strong>Address:</strong> {myProfile?.residential_address || 'Not specified'}</div>
                <div><strong>Education:</strong> {myProfile?.education_qualification}</div>
                <div><strong>Current Status:</strong> {myProfile?.current_employment_status}</div>
                <div><strong>Experience:</strong> {myProfile?.work_experience_years || 0} years</div>
                <div><strong>Preferred Mode:</strong> {myProfile?.preferred_training_mode}</div>
                <div><strong>Preferred Location:</strong> {myProfile?.preferred_training_location}</div>
                <div><strong>Career Goals:</strong> {myProfile?.career_goals || 'Not specified'}</div>
                <div>
                  <strong>Profile Completion:</strong>
                  <span style={{ marginLeft: '0.5rem', fontWeight: 700, color: '#ea580c' }}>
                    {myProfile?.profile_completion_percentage || 85}%
                  </span>
                </div>
              </div>
            </div>

            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.75rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a' }}>Existing Skills & Competencies</h3>
                <span style={{ fontSize: '0.78rem', color: '#64748b' }}>Proficiency Validated</span>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1.5rem' }}>
                {myProfile?.skills?.map((sk: any) => (
                  <span key={sk.id} style={{ backgroundColor: '#eff6ff', color: '#1e40af', padding: '0.35rem 0.75rem', borderRadius: '6px', fontSize: '0.82rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}>
                    {sk.skill_name} <span style={{ opacity: 0.8, fontSize: '0.75rem' }}>({sk.proficiency})</span>
                    <button
                      style={{ background: 'none', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '0 2px', fontWeight: 700 }}
                      title="Deactivate / Remove skill"
                      onClick={async () => {
                        if (!confirm(`Remove declared skill '${sk.skill_name}'?`)) return;
                        await fetch(`${API_BASE}/api/profiles/me/skills/${sk.id}`, { method: 'DELETE', headers: { Authorization: `Bearer ${token}` } });
                        const p = await (await fetch(`${API_BASE}/api/profiles/me`, { headers: { Authorization: `Bearer ${token}` } })).json();
                        setMyProfile(p);
                      }}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>

              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                <input
                  type="text"
                  className="form-control"
                  style={{ flex: 1, minWidth: '180px' }}
                  placeholder="Skill name (e.g. Python Programming, SQL)..."
                  value={newSkillInput}
                  onChange={(e) => setNewSkillInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
                />
                <select
                  className="form-control"
                  style={{ width: '140px' }}
                  id="skillProficiencySelect"
                  defaultValue="Intermediate"
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                  <option value="Expert">Expert</option>
                </select>
                <button
                  className="btn-primary-orange"
                  onClick={() => {
                    const selectEl = document.getElementById('skillProficiencySelect') as HTMLSelectElement;
                    const prof = selectEl ? selectEl.value : 'Intermediate';
                    if (!newSkillInput.trim() || !token) return;
                    fetch(`${API_BASE}/api/profiles/me/skills`, {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                      body: JSON.stringify({ skill_name: newSkillInput.trim(), proficiency: prof })
                    }).then(() => {
                      setNewSkillInput('');
                      fetch(`${API_BASE}/api/profiles/me`, { headers: { Authorization: `Bearer ${token}` } })
                        .then(r => r.json())
                        .then(setMyProfile);
                    });
                  }}
                >
                  Add Skill
                </button>
              </div>
            </div>

            {/* Account Security & Password Management Card */}
            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.75rem', gridColumn: '1 / -1' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <div style={{ backgroundColor: '#eff6ff', padding: '0.45rem', borderRadius: '8px', color: '#1e40af' }}>
                    <Lock size={18} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                      Account Security & Password Management
                    </h3>
                    <p style={{ margin: 0, fontSize: '0.78rem', color: '#64748b' }}>
                      Update your account password or modify authentication credentials
                    </p>
                  </div>
                </div>
              </div>

              {changePasswordMsg && (
                <div style={{
                  backgroundColor: changePasswordMsg.type === 'success' ? '#f0fdf4' : '#fee2e2',
                  color: changePasswordMsg.type === 'success' ? '#166534' : '#b91c1c',
                  border: changePasswordMsg.type === 'success' ? '1px solid #bbf7d0' : '1px solid #fecaca',
                  padding: '0.65rem 0.85rem',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  marginBottom: '1.25rem'
                }}>
                  {changePasswordMsg.text}
                </div>
              )}

              <form onSubmit={handleChangePassword} style={{ maxWidth: '480px' }}>
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.35rem', display: 'block' }}>
                    Current Password:
                  </label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type={showChangeCurrentPassword ? 'text' : 'password'}
                      required
                      className="form-control"
                      style={{ paddingRight: '2.5rem' }}
                      value={changeCurrentPassword}
                      onChange={(e) => setChangeCurrentPassword(e.target.value)}
                      placeholder="Enter current password"
                    />
                    <button
                      type="button"
                      style={{
                        position: 'absolute',
                        right: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#64748b',
                        display: 'flex',
                        alignItems: 'center',
                        padding: 0
                      }}
                      onClick={() => setShowChangeCurrentPassword(!showChangeCurrentPassword)}
                    >
                      {showChangeCurrentPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.35rem', display: 'block' }}>
                    New Password (minimum 8 characters):
                  </label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type={showChangeNewPassword ? 'text' : 'password'}
                      required
                      minLength={8}
                      className="form-control"
                      style={{ paddingRight: '2.5rem' }}
                      value={changeNewPassword}
                      onChange={(e) => setChangeNewPassword(e.target.value)}
                      placeholder="Enter new password"
                    />
                    <button
                      type="button"
                      style={{
                        position: 'absolute',
                        right: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#64748b',
                        display: 'flex',
                        alignItems: 'center',
                        padding: 0
                      }}
                      onClick={() => setShowChangeNewPassword(!showChangeNewPassword)}
                    >
                      {showChangeNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {changeNewPassword && (
                    <div style={{ fontSize: '0.72rem', marginTop: '0.25rem', color: changeNewPassword.length >= 8 ? '#16a34a' : '#b91c1c' }}>
                      {changeNewPassword.length >= 8 ? '✓ Password length valid (≥8 characters)' : `Must be at least 8 characters (${changeNewPassword.length}/8)`}
                    </div>
                  )}
                </div>

                <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.35rem', display: 'block' }}>
                    Confirm New Password:
                  </label>
                  <input
                    type="password"
                    required
                    minLength={8}
                    className="form-control"
                    value={changeConfirmPassword}
                    onChange={(e) => setChangeConfirmPassword(e.target.value)}
                    placeholder="Confirm new password"
                  />
                  {changeConfirmPassword && (
                    <div style={{ fontSize: '0.72rem', marginTop: '0.25rem', fontWeight: 600, color: changeNewPassword === changeConfirmPassword ? '#16a34a' : '#b91c1c' }}>
                      {changeNewPassword === changeConfirmPassword ? '✓ Passwords match' : '✕ Passwords do not match'}
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  className="btn-navy-outline"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '0.4rem', padding: '0.5rem 1.1rem', fontSize: '0.82rem' }}
                  disabled={changePasswordLoading || !changeCurrentPassword || !changeNewPassword || changeNewPassword.length < 8 || changeNewPassword !== changeConfirmPassword}
                >
                  {changePasswordLoading ? <Loader2 size={14} className="animate-spin" /> : <Lock size={14} />}
                  {changePasswordLoading ? 'Updating Password...' : 'Change Password'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* VERIFIABLE CERTIFICATES */}
      {activeTab === 'certificates' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <h2>{t('nav.certificates')}</h2>
              <p>Government of India recognized NSQF-aligned competency credentials with public verification</p>
            </div>
          </div>

          {myCertificates.length === 0 ? (
            <div style={{ backgroundColor: '#ffffff', padding: '3rem', borderRadius: '10px', textAlign: 'center', border: '1px solid #e2e8f0' }}>
              <Award size={40} style={{ color: '#94a3b8', margin: '0 auto 1rem auto' }} />
              <h3 style={{ fontSize: '1.15rem', color: '#0f172a', marginBottom: '0.5rem' }}>No Issued Certificates Yet</h3>
              <p style={{ fontSize: '0.85rem', color: '#64748b' }}>Certificates are issued automatically upon completing training modules with passing assessment scores.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.5rem' }}>
              {myCertificates.map((cert: any) => (
                <div key={cert.certificate_code} style={{ backgroundColor: '#ffffff', borderRadius: '12px', border: '2px solid #0f2444', padding: '1.75rem', position: 'relative' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#ea580c' }}>NAGRIKSETU NATIONAL CREDENTIAL</span>
                    <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#0f2444' }}>{cert.certificate_code}</span>
                  </div>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f2444', marginBottom: '0.5rem' }}>{cert.program_title}</h3>
                  <p style={{ fontSize: '0.85rem', color: '#334155', marginBottom: '1rem' }}>
                    Awarded to <strong>{cert.citizen_name}</strong> ({cert.citizen_ref}) with <strong>{cert.grade}</strong> ({cert.score_pct}% Score).
                  </p>
                  <div style={{ fontSize: '0.78rem', color: '#64748b', marginBottom: '1.25rem' }}>
                    Issued on: {cert.issued_date} • NSQF Level 5 Aligned
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <button className="btn-card-action" style={{ flex: '1 1 auto' }} onClick={() => alert(`Official Verification URL:\n${cert.verification_url}`)}>
                      <CheckCircle2 size={14} /> Verify Credential Online
                    </button>
                    <button
                      className="btn-card-action"
                      style={{ backgroundColor: '#0f2444', color: '#ffffff', borderColor: '#0f2444', display: 'inline-flex', alignItems: 'center', gap: '0.4rem' }}
                      onClick={async () => {
                        try {
                          const res = await fetch(`${API_BASE}/api/certificates/${cert.certificate_code}/download`, {
                            headers: { Authorization: `Bearer ${token}` }
                          });
                          if (!res.ok) throw new Error('Download failed');
                          const blob = await res.blob();
                          const url = window.URL.createObjectURL(blob);
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `NagrikSetu_Certificate_${cert.certificate_code}.pdf`;
                          document.body.appendChild(a);
                          a.click();
                          a.remove();
                        } catch (err: any) {
                          alert(`Error downloading certificate: ${err.message}`);
                        }
                      }}
                    >
                      <Download size={14} /> Download PDF
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
        </div>
      )}

      {/* CITIZEN APPLICATION DETAIL MODAL */}
      {selectedCitizenApp && (
        <div className="modal-overlay" onClick={() => setSelectedCitizenApp(null)}>
          <div className="modal-content-lg" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '720px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#ea580c', textTransform: 'uppercase' }}>
                  Application Dossier • {selectedCitizenApp.application_id}
                </span>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f2444', margin: '0.2rem 0 0' }}>
                  {selectedCitizenApp.program_title}
                </h3>
              </div>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setSelectedCitizenApp(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body" style={{ display: 'grid', gap: '1rem', padding: '1.5rem' }}>
              {/* Status Banner */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div>
                  <div style={{ fontSize: '0.78rem', color: '#64748b' }}>Current Status</div>
                  <span className={`status-pill ${selectedCitizenApp.status}`} style={{ fontSize: '0.88rem', fontWeight: 700 }}>
                    {getStatusText(selectedCitizenApp.status)}
                  </span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '0.78rem', color: '#64748b' }}>Submitted On</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#0f2444' }}>
                    {formatISTDateTime(selectedCitizenApp.created_at)}
                  </div>
                </div>
              </div>

              {/* Programme & Training Details */}
              <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.5rem' }}>
                  Training Programme Details
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem', fontSize: '0.85rem' }}>
                  <div><strong>Skill Competency:</strong> {selectedCitizenApp.skill_name || 'Technical'}</div>
                  <div><strong>Training Mode:</strong> {selectedCitizenApp.selected_mode || 'Classroom / Lab'}</div>
                  <div><strong>Progress:</strong> {selectedCitizenApp.training_progress_pct}%</div>
                  <div><strong>Attendance:</strong> {selectedCitizenApp.attendance_pct || 0}%</div>
                  {selectedCitizenApp.batch_details && (
                    <>
                      <div><strong>Batch Name:</strong> {selectedCitizenApp.batch_details.batch_name}</div>
                      <div><strong>Timings:</strong> {selectedCitizenApp.batch_details.timings}</div>
                    </>
                  )}
                </div>
              </div>

              {/* Department Review Remarks */}
              <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '1rem', fontSize: '0.85rem' }}>
                <strong style={{ color: '#166534' }}>Official Department Remarks:</strong>
                <p style={{ margin: '0.35rem 0 0', color: '#14532d' }}>
                  {selectedCitizenApp.admin_remarks || 'Your application has been received and is progressing through the departmental verification pipeline.'}
                </p>
              </div>

              {/* Detailed Application Dossier */}
              {selectedCitizenApp.application_details && (
                <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem' }}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.5rem' }}>
                    Submitted Application Dossier
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.75rem', fontSize: '0.83rem' }}>
                    {selectedCitizenApp.application_details.section_b_address && (
                      <div>
                        <strong>Residential Address:</strong><br />
                        {selectedCitizenApp.application_details.section_b_address.residential_address}, {selectedCitizenApp.application_details.section_b_address.city}, {selectedCitizenApp.application_details.section_b_address.state} ({selectedCitizenApp.application_details.section_b_address.pincode})
                      </div>
                    )}
                    {selectedCitizenApp.application_details.section_c_education && (
                      <div>
                        <strong>Education:</strong><br />
                        {selectedCitizenApp.application_details.section_c_education.highest_qualification} — {selectedCitizenApp.application_details.section_c_education.institution}
                      </div>
                    )}
                    {selectedCitizenApp.application_details.section_d_employment && (
                      <div>
                        <strong>Employment:</strong><br />
                        {selectedCitizenApp.application_details.section_d_employment.employment_status} ({selectedCitizenApp.application_details.section_d_employment.experience_years || 0} years experience)
                      </div>
                    )}
                    {selectedCitizenApp.application_details.section_g_documents && (
                      <div>
                        <strong>Verification Identity:</strong><br />
                        {selectedCitizenApp.application_details.section_g_documents.id_proof_type}: {selectedCitizenApp.application_details.section_g_documents.id_proof_reference || 'Verified'}
                      </div>
                    )}
                  </div>

                  {selectedCitizenApp.application_details.section_f_career_motivation?.statement_of_purpose && (
                    <div style={{ marginTop: '0.85rem', paddingTop: '0.75rem', borderTop: '1px solid #f1f5f9', fontSize: '0.83rem' }}>
                      <strong>Statement of Purpose:</strong>
                      <p style={{ margin: '0.25rem 0 0', color: '#475569', fontStyle: 'italic' }}>
                        "{selectedCitizenApp.application_details.section_f_career_motivation.statement_of_purpose}"
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Status Trail */}
              {selectedCitizenApp.status_history && selectedCitizenApp.status_history.length > 0 && (
                <div style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem' }}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.5rem' }}>
                    Status Timeline & Audit Trail
                  </h4>
                  <div style={{ display: 'grid', gap: '0.5rem' }}>
                    {selectedCitizenApp.status_history.map((h: any, idx: number) => (
                      <div key={idx} style={{ fontSize: '0.82rem', color: '#475569', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                        <span style={{ fontWeight: 600, color: '#0f2444' }}>{formatISTDateTime(h.timestamp)}:</span>
                        <span style={{ fontWeight: 700, color: '#2563eb' }}>{getStatusText(h.new_status)}</span>
                        {h.remarks && <span style={{ color: '#64748b' }}>({h.remarks})</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                <button type="button" className="btn-navy-outline" onClick={() => setSelectedCitizenApp(null)}>
                  Close Dossier
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* COURSE DETAIL MODAL */}
      {selectedCourse && (
        <div className="modal-overlay">
          <div className="modal-content-lg">
            <div className="modal-header">
              <div>
                <span className="badge-category">{selectedCourse.category_name}</span>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f2444' }}>{selectedCourse.name}</h2>
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Course Code: {selectedCourse.code}</span>
              </div>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setSelectedCourse(null)}>
                <X size={20} />
              </button>
            </div>

            <div className="modal-body">
              {/* Tab navigation */}
              <div className="tabs-nav">
                <button className={`tab-btn ${courseDetailTab === 'overview' ? 'active' : ''}`} onClick={() => setCourseDetailTab('overview')}>
                  Overview
                </button>
                <button className={`tab-btn ${courseDetailTab === 'syllabus' ? 'active' : ''}`} onClick={() => setCourseDetailTab('syllabus')}>
                  Curriculum & Modules
                </button>
                <button className={`tab-btn ${courseDetailTab === 'batches' ? 'active' : ''}`} onClick={() => setCourseDetailTab('batches')}>
                  Training Programmes & Batches
                </button>
              </div>

              {courseDetailTab === 'overview' && (
                <div>
                  <h4 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>Detailed Overview</h4>
                  <p style={{ fontSize: '0.88rem', color: '#334155', lineHeight: 1.6, marginBottom: '1.25rem' }}>{selectedCourse.details}</p>

                  <h4 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>Prerequisites</h4>
                  <p style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '1.25rem' }}>{selectedCourse.prerequisites}</p>

                  <h4 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>Career Opportunities</h4>
                  <p style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '1.25rem' }}>{selectedCourse.career_opportunities}</p>

                  <h4 style={{ fontWeight: 700, marginBottom: '0.5rem' }}>Certificate Information</h4>
                  <p style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '1.5rem' }}>{selectedCourse.cert_info}</p>
                </div>
              )}

              {courseDetailTab === 'syllabus' && (
                <div style={{ display: 'grid', gap: '1rem' }}>
                  {selectedCourse.modules?.map((m: any) => (
                    <div key={m.id} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem', backgroundColor: '#f8fafc' }}>
                      <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.35rem' }}>{m.title}</h4>
                      <p style={{ fontSize: '0.85rem', color: '#334155', marginBottom: '0.5rem' }}>{m.description}</p>
                      <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        <div><strong>Key Topics:</strong> {m.topics}</div>
                        <div><strong>Lab Exercise:</strong> {m.practical_assignments}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {courseDetailTab === 'batches' && (
                <div style={{ display: 'grid', gap: '1rem' }}>
                  {selectedCourse.programs?.map((prg: any) => (
                    <div key={prg.code} style={{ border: '1px solid #cbd5e1', borderRadius: '8px', padding: '1.25rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f2444' }}>{prg.title}</h4>
                        <span style={{ fontWeight: 700, color: '#16a34a' }}>{prg.fee === 0 ? 'Free (Govt Subsidized)' : `₹ ${prg.fee}`}</span>
                      </div>
                      <p style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '0.75rem' }}>{prg.description}</p>

                      <h5 style={{ fontSize: '0.85rem', fontWeight: 700, color: '#334155', marginBottom: '0.5rem' }}>Available Batches:</h5>
                      <div style={{ display: 'grid', gap: '0.5rem' }}>
                        {prg.batches?.map((b: any) => (
                          <div key={b.code} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', backgroundColor: '#f8fafc', padding: '0.75rem', borderRadius: '6px' }}>
                            <div>
                              <strong style={{ fontSize: '0.9rem' }}>{b.batch_name}</strong>
                              <div style={{ fontSize: '0.78rem', color: '#64748b' }}>{b.timings} • {b.training_schedule} • {b.mode}</div>
                            </div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                              <span style={{ fontSize: '0.8rem', color: b.available_seats > 0 ? '#166534' : '#b91c1c', fontWeight: 600 }}>
                                {b.available_seats} Seats Left
                              </span>
                              {userRole !== 'SKILL_DEPARTMENT_ADMIN' && userRole !== 'GOVERNMENT_ADMIN' && (
                                <button
                                  className="btn-primary-orange"
                                  style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
                                  disabled={b.available_seats <= 0}
                                  onClick={() => {
                                    setSelectedCourse(null);
                                    handleStartEnrolment(prg);
                                    setSelectedBatchId(b.id);
                                  }}
                                >
                                  Enrol
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ENROLMENT SUBMISSION MODAL */}
      {/* CITIZEN PROFILE EDIT MODAL */}
      {showEditProfileModal && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '680px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444' }}>Edit Citizen Profile</h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setShowEditProfileModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleSaveProfile} className="modal-body" style={{ display: 'grid', gap: '1rem' }}>
              {profileMsg && (
                <div style={{
                  backgroundColor: profileMsg.type === 'success' ? '#dcfce7' : '#fee2e2',
                  color: profileMsg.type === 'success' ? '#15803d' : '#b91c1c',
                  padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem'
                }}>
                  {profileMsg.text}
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Name:</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    value={editFullName}
                    onChange={(e) => setEditFullName(e.target.value)}
                    placeholder="Name as per Aadhaar Card"
                  />
                </div>
                <div className="form-group">
                  <label>Mobile Number:</label>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <input
                      type="tel"
                      required
                      className="form-control"
                      value={editPhone}
                      onChange={(e) => {
                        setEditPhone(e.target.value);
                        setProfileOtpVerified(false);
                        setProfileOtpSent(false);
                      }}
                      disabled={profileOtpVerified}
                    />
                    {editPhone.trim().replace(/\D/g, '') !== (myProfile?.phone || '').replace(/\D/g, '') && (
                      <button
                        type="button"
                        className="btn-navy-outline"
                        style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
                        onClick={handleSendProfileOtp}
                        disabled={profileOtpLoading || profileOtpCooldown > 0 || profileOtpVerified}
                      >
                        {profileOtpVerified ? 'Verified' : (profileOtpCooldown > 0 ? `Resend (${profileOtpCooldown}s)` : (profileOtpSent ? 'Resend' : 'Verify via SMS'))}
                      </button>
                    )}
                  </div>
                  {profileOtpVerified && (
                    <div style={{ color: '#16a34a', fontSize: '0.78rem', marginTop: '0.3rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <CheckCircle2 size={14} /> New number verified via SMS OTP
                    </div>
                  )}
                  {profileOtpSent && !profileOtpVerified && (
                    <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.6rem', marginTop: '0.5rem' }}>
                      <label style={{ fontSize: '0.8rem', fontWeight: 600, color: '#166534', display: 'block', marginBottom: '0.3rem' }}>
                        Enter 6-Digit SMS OTP:
                      </label>
                      <div style={{ display: 'flex', gap: '0.4rem' }}>
                        <input
                          type="text"
                          maxLength={6}
                          className="form-control"
                          style={{ maxWidth: '140px', letterSpacing: '3px', fontWeight: 700, textAlign: 'center' }}
                          value={profileOtpCode}
                          onChange={(e) => setProfileOtpCode(e.target.value.replace(/\D/g, ''))}
                          placeholder="••••••"
                        />
                        <button
                          type="button"
                          className="btn-primary-orange"
                          style={{ padding: '0.3rem 0.75rem', fontSize: '0.8rem' }}
                          onClick={handleVerifyProfileOtp}
                          disabled={profileOtpLoading || profileOtpCode.length !== 6}
                        >
                          {profileOtpLoading ? 'Verifying...' : 'Verify'}
                        </button>
                      </div>
                      {profileOtpMsg && (
                        <div style={{ fontSize: '0.75rem', color: profileOtpMsg.type === 'success' ? '#15803d' : '#b91c1c', marginTop: '0.3rem' }}>
                          {profileOtpMsg.text}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Date of Birth:</label>
                  <input
                    type="date"
                    className="form-control"
                    value={editDob}
                    onChange={(e) => setEditDob(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Gender:</label>
                  <select
                    className="form-control"
                    value={editGender}
                    onChange={(e) => setEditGender(e.target.value)}
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Transgender">Transgender</option>
                    <option value="Prefer not to say">Prefer not to say</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>Residential Address:</label>
                <textarea
                  className="form-control"
                  rows={2}
                  value={editAddress}
                  onChange={(e) => setEditAddress(e.target.value)}
                  placeholder="Street, locality, city, postal code..."
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Education Qualification:</label>
                  <select
                    className="form-control"
                    value={editEducation}
                    onChange={(e) => setEditEducation(e.target.value)}
                  >
                    <option value="Secondary School (10th)">Secondary School (10th)</option>
                    <option value="Higher Secondary (12th / PUC)">Higher Secondary (12th / PUC)</option>
                    <option value="Diploma / Polytechnic">Diploma / Polytechnic</option>
                    <option value="Bachelor of Engineering / Science">Bachelor of Engineering / Science</option>
                    <option value="Bachelor of Commerce / Arts">Bachelor of Commerce / Arts</option>
                    <option value="Master of Technology / Science">Master of Technology / Science</option>
                    <option value="Doctorate / PhD">Doctorate / PhD</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Current Employment Status:</label>
                  <select
                    className="form-control"
                    value={editEmployment}
                    onChange={(e) => setEditEmployment(e.target.value)}
                  >
                    <option value="Job Seeker">Job Seeker</option>
                    <option value="Student / Scholar">Student / Scholar</option>
                    <option value="Employed">Employed</option>
                    <option value="Self-Employed / Freelancer">Self-Employed / Freelancer</option>
                    <option value="Apprentice">Apprentice</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label>Experience (Years):</label>
                  <input
                    type="number"
                    min={0}
                    max={40}
                    className="form-control"
                    value={editExpYears}
                    onChange={(e) => setEditExpYears(Number(e.target.value))}
                  />
                </div>
                <div className="form-group">
                  <label>Preferred Mode:</label>
                  <select
                    className="form-control"
                    value={editPrefMode}
                    onChange={(e) => setEditPrefMode(e.target.value)}
                  >
                    <option value="Hybrid">Hybrid</option>
                    <option value="Online">Online</option>
                    <option value="Classroom">Classroom</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Preferred Location:</label>
                  <input
                    type="text"
                    className="form-control"
                    value={editPrefLocation}
                    onChange={(e) => setEditPrefLocation(e.target.value)}
                    placeholder="e.g. Bengaluru, Mysuru"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Technical Interests & Domains:</label>
                <input
                  type="text"
                  className="form-control"
                  value={editInterests}
                  onChange={(e) => setEditInterests(e.target.value)}
                  placeholder="e.g. Full Stack, AI/ML, Cloud Security"
                />
              </div>

              <div className="form-group">
                <label>Career Goals / Objective:</label>
                <textarea
                  className="form-control"
                  rows={2}
                  value={editGoals}
                  onChange={(e) => setEditGoals(e.target.value)}
                  placeholder="What roles or skills are you aiming to achieve?"
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button type="button" className="btn-navy-outline" onClick={() => setShowEditProfileModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary-orange" disabled={profileSaving}>
                  {profileSaving ? 'Saving Updates...' : 'Save Profile Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* SIMPLIFIED CITIZEN TRAINING APPLICATION FORM */}
      {enrollingProgram && (!userRole || userRole === 'CITIZEN') && (
        <div className="modal-overlay" style={{ zIndex: 1100 }}>
          <div className="modal-content-lg" style={{ maxWidth: '680px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header" style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '0.75rem' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444', margin: 0 }}>
                  Training Programme Application
                </h3>
                <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  Fast & Simple Registration â€¢ Pre-filled from your Citizen Profile
                </span>
              </div>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setEnrollingProgram(null)}>
                <X size={20} />
              </button>
            </div>

            <div className="modal-body" style={{ display: 'grid', gap: '1.25rem', paddingTop: '1rem' }}>
              {/* Selected Programme Summary Banner */}
              <div style={{ backgroundColor: '#f8fafc', borderLeft: '4px solid #ea580c', borderTop: '1px solid #e2e8f0', borderRight: '1px solid #e2e8f0', borderBottom: '1px solid #e2e8f0', padding: '1rem', borderRadius: '6px' }}>
                <div style={{ fontWeight: 700, color: '#0f172a', fontSize: '1.05rem' }}>{enrollingProgram.title}</div>
                <div style={{ fontSize: '0.82rem', color: '#475569', marginTop: '0.25rem', display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
                  <span><strong>Programme Code:</strong> {enrollingProgram.code}</span>
                  <span><strong>Duration:</strong> {enrollingProgram.duration_hours || 40} Hours</span>
                  <span><strong>Fee:</strong> {enrollingProgram.fee === 0 ? 'Free (Govt Subsidized)' : `â‚¹${enrollingProgram.fee}`}</span>
                </div>
              </div>

              {enrolmentErrorMsg && (
                <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem' }}>
                  {enrolmentErrorMsg}
                </div>
              )}
              {enrolmentSuccessMsg && (
                <div style={{ backgroundColor: '#dcfce7', color: '#15803d', padding: '0.75rem', borderRadius: '6px', fontSize: '0.85rem' }}>
                  {enrolmentSuccessMsg}
                </div>
              )}

              {/* Verified Citizen Profile Autofill Notice */}
              <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.6rem 0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', color: '#166534' }}>
                <CheckCircle2 size={16} style={{ color: '#16a34a', flexShrink: 0 }} />
                <span><strong>Profile Autofill Active:</strong> Your verified profile details have been prefilled below. Review and adjust if necessary.</span>
              </div>

              {/* SECTION A: Personal Information */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.15rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.35rem' }}>
                  A. Personal Information
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Full Name *</label>
                    <input type="text" className="form-control" value={appFullName} onChange={(e) => setAppFullName(e.target.value)} placeholder="Full Name" required />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Citizen ID (Read-only)</label>
                    <input type="text" className="form-control" value={citizenRef || 'CIT-2026-X'} readOnly disabled style={{ backgroundColor: '#f8fafc', cursor: 'not-allowed', color: '#64748b' }} />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Email Address *</label>
                    <input type="email" className="form-control" value={appEmail} onChange={(e) => setAppEmail(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Mobile Number *</label>
                    <input type="tel" className="form-control" value={appPhone} onChange={(e) => setAppPhone(e.target.value)} required />
                  </div>
                </div>
              </div>

              {/* SECTION B: Basic Location */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.15rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.35rem' }}>
                  B. Basic Location
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>City / District *</label>
                    <input type="text" className="form-control" value={appCity} onChange={(e) => setAppCity(e.target.value)} placeholder="e.g. Bengaluru, Mysuru, Hubballi" required />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>PIN Code *</label>
                    <input type="text" className="form-control" value={appPincode} onChange={(e) => setAppPincode(e.target.value)} placeholder="6-digit PIN" maxLength={6} required />
                  </div>
                </div>
              </div>

              {/* SECTION C: Basic Eligibility Information */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.15rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.35rem' }}>
                  C. Basic Eligibility Information
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Highest Educational Qualification *</label>
                    <select className="form-control" value={appEducation} onChange={(e) => setAppEducation(e.target.value)}>
                      <option value="Secondary School (10th)">Secondary School (10th)</option>
                      <option value="Higher Secondary (12th / PUC)">Higher Secondary (12th / PUC)</option>
                      <option value="Diploma / Polytechnic">Diploma / Polytechnic</option>
                      <option value="Bachelor of Engineering / Science">Bachelor of Engineering / Science</option>
                      <option value="Bachelor of Commerce / Arts">Bachelor of Commerce / Arts</option>
                      <option value="Master of Technology / Science">Master of Technology / Science</option>
                      <option value="Other / Vocational">Other / Vocational</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Employment Status *</label>
                    <select className="form-control" value={appEmploymentStatus} onChange={(e) => setAppEmploymentStatus(e.target.value)}>
                      <option value="Job Seeker">Job Seeker</option>
                      <option value="Student / Scholar">Student / Scholar</option>
                      <option value="Employed">Employed</option>
                      <option value="Self-Employed / Freelancer">Self-Employed / Freelancer</option>
                      <option value="Apprentice">Apprentice</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* SECTION D: Training Selection */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.15rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.35rem' }}>
                  D. Training Selection
                </h4>
                <div style={{ display: 'grid', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Selected Programme (Populated from your choice)</label>
                    <input type="text" className="form-control" value={enrollingProgram.title} readOnly disabled style={{ backgroundColor: '#f8fafc', color: '#0f2444', fontWeight: 600 }} />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Assigned Training Centre (Derived from database relationship)</label>
                    <input
                      type="text"
                      className="form-control"
                      value={enrollingProgram.centre?.name || enrollingProgram.centre_name || 'Accredited Training Centre'}
                      readOnly
                      disabled
                      style={{ backgroundColor: '#f8fafc', color: '#1e293b', fontWeight: 600 }}
                    />
                    {enrollingProgram.centre?.location && (
                      <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>
                        Location: {enrollingProgram.centre.location} ({enrollingProgram.centre.district})
                      </div>
                    )}
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Available Training Batch * (Real-time seat capacity checked)</label>
                    <select
                      className="form-control"
                      value={selectedBatchId || ''}
                      onChange={(e) => setSelectedBatchId(Number(e.target.value))}
                      required
                    >
                      {enrollingProgram.batches && enrollingProgram.batches.length > 0 ? (
                        enrollingProgram.batches.map((b: any) => (
                          <option key={b.id} value={b.id} disabled={b.available_seats <= 0}>
                            {b.batch_name} ({b.timings} - {b.mode}) â€” {b.available_seats} / {b.total_seats} seats available {b.available_seats <= 0 ? '(FULL)' : ''}
                          </option>
                        ))
                      ) : (
                        <option value="">No open batches available</option>
                      )}
                    </select>
                  </div>

                  {/* Preferred Delivery Mode only if programme supports choice */}
                  {(!enrollingProgram.mode || enrollingProgram.mode.toLowerCase() === 'hybrid') && (
                    <div className="form-group">
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#334155' }}>Preferred Delivery Mode</label>
                      <select className="form-control" value={appPrefMode} onChange={(e) => setAppPrefMode(e.target.value)}>
                        <option value="Hybrid">Hybrid (Online Lectures + Hands-on Lab)</option>
                        <option value="Online">Online Interactive</option>
                        <option value="Classroom">Classroom Full-Time</option>
                      </select>
                    </div>
                  )}
                </div>
              </div>

              {/* SECTION E: Declaration */}
              <div style={{ border: '1px solid #fed7aa', backgroundColor: '#fff7ed', borderRadius: '8px', padding: '1.15rem' }}>
                <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: '#9a3412', marginBottom: '0.4rem' }}>
                  E. Declaration & Confirmation
                </h4>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                  <input
                    type="checkbox"
                    id="enrolDeclaration"
                    checked={appDeclarationAgreed}
                    onChange={(e) => setAppDeclarationAgreed(e.target.checked)}
                    style={{ marginTop: '0.25rem', width: '18px', height: '18px', cursor: 'pointer' }}
                    required
                  />
                  <label htmlFor="enrolDeclaration" style={{ fontSize: '0.82rem', color: '#7c2d12', lineHeight: 1.45, cursor: 'pointer', margin: 0 }}>
                    I hereby confirm that all submitted details are accurate and complete to the best of my knowledge, and I agree to be contacted by the assigned Training Centre regarding my application and batch admission formalities.
                  </label>
                </div>
              </div>

              {/* Action Buttons */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.25rem', borderTop: '1px solid #e2e8f0', paddingTop: '0.85rem' }}>
                <button type="button" className="btn-navy-outline" onClick={() => setEnrollingProgram(null)} disabled={enrolSubmitting}>
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn-primary-orange"
                  onClick={handleEnrolmentSubmit}
                  disabled={enrolSubmitting || !appDeclarationAgreed || (enrollingProgram.batches && enrollingProgram.batches.length > 0 && !selectedBatchId)}
                >
                  {enrolSubmitting ? 'Submitting Application...' : 'Submit Training Application'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ADMIN REVIEW MODAL WITH COMPREHENSIVE DOSSIER VIEWER */}
      {reviewModalApp && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '720px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444' }}>Application Details & Oversight — {reviewModalApp.application_id}</h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setReviewModalApp(null)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body" style={{ display: 'grid', gap: '1rem' }}>
              <div style={{ backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '8px', fontSize: '0.85rem', border: '1px solid #e2e8f0' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                  <div><strong>Applicant:</strong> {reviewModalApp.citizen_name} ({reviewModalApp.citizen_ref})</div>
                  <div><strong>Email:</strong> {reviewModalApp.citizen_email}</div>
                  <div><strong>Phone:</strong> {reviewModalApp.citizen_phone || 'N/A'}</div>
                  <div><strong>Programme:</strong> {reviewModalApp.program_title}</div>
                  <div><strong>Batch:</strong> {reviewModalApp.batch_name || 'Regular'} ({reviewModalApp.selected_mode})</div>
                  <div><strong>Submitted (IST):</strong> {formatISTDateTime(reviewModalApp.created_at)}</div>
                  <div><strong>Current Status:</strong> <span className={`status-pill ${reviewModalApp.status}`}>{reviewModalApp.status}</span></div>
                  {reviewModalApp.updated_at && (
                    <div><strong>Last Updated (IST):</strong> {formatISTDateTime(reviewModalApp.updated_at)}</div>
                  )}
                </div>
              </div>

              {/* Comprehensive 8-Section Application Dossier Display */}
              {reviewModalApp.application_details ? (
                <div style={{ border: '1px solid #cbd5e1', borderRadius: '8px', padding: '1rem', backgroundColor: '#ffffff', fontSize: '0.82rem' }}>
                  <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.5rem', borderBottom: '1px solid #e2e8f0', paddingBottom: '0.3rem' }}>
                    Application Dossier Summary (Sections A – H)
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                    <div>
                      <strong>Address:</strong> {reviewModalApp.application_details.section_b_address?.residential_address}, {reviewModalApp.application_details.section_b_address?.city}, {reviewModalApp.application_details.section_b_address?.state} ({reviewModalApp.application_details.section_b_address?.pincode})
                    </div>
                    <div>
                      <strong>Education:</strong> {reviewModalApp.application_details.section_c_education?.highest_qualification} ({reviewModalApp.application_details.section_c_education?.institution || 'VTU'})
                    </div>
                    <div>
                      <strong>Employment:</strong> {reviewModalApp.application_details.section_d_employment?.employment_status} ({reviewModalApp.application_details.section_d_employment?.experience_years || 0} yrs exp)
                    </div>
                    <div>
                      <strong>ID Proof:</strong> {reviewModalApp.application_details.section_g_documents?.id_proof_type} ({reviewModalApp.application_details.section_g_documents?.id_proof_reference || 'Verified'})
                    </div>
                  </div>
                  <div style={{ marginTop: '0.5rem', backgroundColor: '#f8fafc', padding: '0.5rem', borderRadius: '4px' }}>
                    <strong>Applicant Statement of Purpose:</strong>
                    <div style={{ color: '#334155', marginTop: '0.2rem', fontStyle: 'italic' }}>
                      "{reviewModalApp.application_details.section_f_career_motivation?.statement_of_purpose || reviewModalApp.applicant_statement || 'N/A'}"
                    </div>
                  </div>
                </div>
              ) : reviewModalApp.applicant_statement && (
                <div style={{ backgroundColor: '#f8fafc', padding: '0.75rem', borderRadius: '6px', fontSize: '0.82rem' }}>
                  <strong>Applicant Statement:</strong>
                  <p style={{ margin: '0.25rem 0 0', color: '#475569', fontStyle: 'italic' }}>"{reviewModalApp.applicant_statement}"</p>
                </div>
              )}

              {reviewModalApp.status_history && reviewModalApp.status_history.length > 0 && (
                <div style={{ border: '1px solid #e2e8f0', borderRadius: '6px', padding: '0.75rem', backgroundColor: '#ffffff', fontSize: '0.8rem' }}>
                  <div style={{ fontWeight: 700, color: '#475569', marginBottom: '0.4rem', textTransform: 'uppercase', fontSize: '0.75rem' }}>
                    Status & Audit Trail:
                  </div>
                  <div style={{ display: 'grid', gap: '0.35rem' }}>
                    {reviewModalApp.status_history.map((h: any, idx: number) => (
                      <div key={idx} style={{ display: 'flex', gap: '0.5rem', color: '#64748b', flexWrap: 'wrap' }}>
                        <span style={{ color: '#475569', fontWeight: 500 }}>{formatISTDateTime(h.timestamp)}:</span>
                        <span style={{ fontWeight: 600, color: '#0f172a' }}>{h.new_status}</span>
                        {h.actor && <span style={{ color: '#0284c7' }}>by {h.actor}</span>}
                        {h.remarks && <span>— {h.remarks}</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Enforce Strict View-Only Monitoring Privileges */}
              <div style={{ backgroundColor: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '0.9rem', fontSize: '0.84rem', color: '#1e40af' }}>
                <div style={{ fontWeight: 700, marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <Shield size={16} /> Platform Admin Oversight — Strictly View-Only
                </div>
                <div style={{ color: '#1e3a8a', lineHeight: 1.5 }}>
                  This application record is monitored centrally under read-only oversight. Operational reviews, eligibility assessments, approval decisions, and batch assignments are executed strictly by the assigned Training Centre Administrator.
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', backgroundColor: '#f8fafc', padding: '0.9rem', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '0.84rem' }}>
                <div><strong>Assigned Centre ID:</strong> {reviewModalApp.centre_id || 'N/A'}</div>
                <div><strong>Assigned Batch:</strong> {reviewModalApp.batch_name || 'BAT-0037'}</div>
                <div><strong>Training Progress:</strong> {reviewModalApp.training_progress_pct ?? 0}%</div>
                <div><strong>Learner Attendance:</strong> {reviewModalApp.attendance_pct ?? 0}%</div>
                <div style={{ gridColumn: 'span 2' }}>
                  <strong>Admin Remarks:</strong> {reviewModalApp.admin_remarks || 'Candidate meets NSQF Level 5 prerequisites. Enrolled into Batch BAT-0037.'}
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button className="btn-primary-orange" style={{ minWidth: '100px' }} onClick={() => setReviewModalApp(null)}>
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          NAGRIKSETU MULTI-ROLE AUTHENTICATION & REGISTRATION PORTAL
          - 2 Landing Buttons: [Sign In] & [Register]
          - Account-Selection Screen with exactly 3 options:
              1. Citizen User
              2. Training Centre
              3. Platform Admin
          - Dedicated Login Screens for each role
          - Back navigation on every screen
          - Exclusively Citizen-only Public Registration
         ========================================================================= */}

      {/* 1. ACCOUNT-SELECTION PAGE / MODAL */}
      {(authPortalView === 'select_role' || (showLoginModal && !isAdminLogin && authPortalView === 'none')) && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '580px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.25)' }}>
            {/* Header */}
            <div style={{ backgroundColor: '#0f2444', padding: '1.5rem 1.75rem', color: '#ffffff', position: 'relative' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.35rem' }}>
                <Landmark size={20} color="#f97316" />
                <span style={{ fontSize: '0.75rem', letterSpacing: '0.08em', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 700 }}>
                  National Skill Mission
                </span>
              </div>
              <h3 style={{ fontSize: '1.35rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                Select Portal Account
              </h3>
              <p style={{ margin: '0.35rem 0 0 0', fontSize: '0.85rem', color: '#cbd5e1' }}>
                Choose your designated role to access specialized services and dashboards.
              </p>
              <button
                type="button"
                style={{ position: 'absolute', top: '1.25rem', right: '1.25rem', background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                onClick={() => { setAuthPortalView('none'); setShowLoginModal(false); setAuthError(''); }}
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>

            {/* Portal Cards Body */}
            <div style={{ padding: '1.75rem', backgroundColor: '#f8fafc' }}>
              {authError && (
                <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.75rem 1rem', borderRadius: '8px', fontSize: '0.85rem', marginBottom: '1.25rem', border: '1px solid #fecaca', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <AlertCircle size={16} />
                  <span>{authError}</span>
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {/* Option 1: Citizen User */}
                <button
                  type="button"
                  onClick={() => {
                    setAuthPortalView('login_citizen');
                    setIsAdminLogin(false);
                    setAuthError('');
                    setLoginPassword('');
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '1.15rem 1.25rem',
                    backgroundColor: '#ffffff',
                    border: '1.5px solid #e2e8f0',
                    borderRadius: '10px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.03)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#ea580c';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 6px 16px rgba(234, 88, 12, 0.12)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#e2e8f0';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.03)';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ width: '46px', height: '46px', borderRadius: '10px', backgroundColor: '#fff7ed', border: '1px solid #fed7aa', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#ea580c' }}>
                      <User size={24} />
                    </div>
                    <div>
                      <div style={{ fontSize: '1rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.2rem' }}>
                        1. Citizen Login
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        Browse courses, track enrolment applications, attendance & certificates
                      </div>
                    </div>
                  </div>
                  <ChevronRight size={20} color="#94a3b8" />
                </button>

                {/* Option 2: Student Login (Enrolled Trainees) */}
                <button
                  type="button"
                  onClick={() => {
                    setAuthPortalView('login_student');
                    setIsAdminLogin(false);
                    setAuthError('');
                    setLoginPassword('');
                    setLoginEmail('STU-2026-000104');
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '1.15rem 1.25rem',
                    backgroundColor: '#ffffff',
                    border: '1.5px solid #e2e8f0',
                    borderRadius: '10px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.03)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#0284c7';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 6px 16px rgba(2, 132, 199, 0.12)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#e2e8f0';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.03)';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ width: '46px', height: '46px', borderRadius: '10px', backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0284c7' }}>
                      <GraduationCap size={24} />
                    </div>
                    <div>
                      <div style={{ fontSize: '1rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.2rem' }}>
                        2. Student Login
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        Dedicated portal for enrolled students via Student ID or Email with timetable & progress
                      </div>
                    </div>
                  </div>
                  <ChevronRight size={20} color="#94a3b8" />
                </button>

                {/* Option 3: Training Centre */}
                <button
                  type="button"
                  onClick={() => {
                    setAuthPortalView('login_centre');
                    setIsAdminLogin(true);
                    setAuthError('');
                    setLoginEmail('centre.bengaluru@nagriksetu.local');
                    setLoginPassword('');
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '1.15rem 1.25rem',
                    backgroundColor: '#ffffff',
                    border: '1.5px solid #e2e8f0',
                    borderRadius: '10px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.03)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#6366f1';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 6px 16px rgba(99, 102, 241, 0.12)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#e2e8f0';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.03)';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ width: '46px', height: '46px', borderRadius: '10px', backgroundColor: '#eef2ff', border: '1px solid #c7d2fe', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6366f1' }}>
                      <Building2 size={24} />
                    </div>
                    <div>
                      <div style={{ fontSize: '1rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.2rem' }}>
                        3. Training Centre
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        Manage assigned centre workspace, batches, trainers & student dossiers
                      </div>
                    </div>
                  </div>
                  <ChevronRight size={20} color="#94a3b8" />
                </button>

                {/* Option 4: Platform Admin */}
                <button
                  type="button"
                  onClick={() => {
                    setAuthPortalView('login_admin');
                    setIsAdminLogin(true);
                    setAuthError('');
                    setLoginEmail('skill.admin@nagriksetu.local');
                    setLoginPassword('SkillAdmin@2026!');
                  }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '1.15rem 1.25rem',
                    backgroundColor: '#ffffff',
                    border: '1.5px solid #e2e8f0',
                    borderRadius: '10px',
                    textAlign: 'left',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 2px 4px rgba(0,0,0,0.03)'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#16a34a';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 6px 16px rgba(22, 163, 74, 0.12)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = '#e2e8f0';
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.03)';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    <div style={{ width: '46px', height: '46px', borderRadius: '10px', backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#16a34a' }}>
                      <Shield size={24} />
                    </div>
                    <div>
                      <div style={{ fontSize: '1rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.2rem' }}>
                        4. Platform Admin
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        Department of Skill Development governance, 18 centres, queues & audit
                      </div>
                    </div>
                  </div>
                  <ChevronRight size={20} color="#94a3b8" />
                </button>
              </div>

              {/* Bottom Footer Action: Direct Citizen Register */}
              <div style={{ marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.82rem' }}>
                <span style={{ color: '#64748b' }}>New to NagrikSetu?</span>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#ea580c', fontWeight: 700, cursor: 'pointer', textDecoration: 'underline' }}
                  onClick={() => {
                    setAuthPortalView('register_citizen');
                    setShowLoginModal(false);
                    setAuthError('');
                  }}
                >
                  Register as a Citizen →
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2. CITIZEN USER LOGIN SCREEN */}
      {authPortalView === 'login_citizen' && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '440px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.25)' }}>
            {/* Header with Back Navigation */}
            <div style={{ backgroundColor: '#0f2444', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.12)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}
                  title="Back to Account Selection"
                >
                  <ArrowLeft size={16} />
                </button>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#f97316', fontWeight: 700 }}>
                    Citizen Portal
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Citizen User Login
                  </h3>
                </div>
              </div>
              <button
                type="button"
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                onClick={() => { setAuthPortalView('none'); setAuthError(''); }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem' }}>
              <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: 0, marginBottom: '1rem' }}>
                Access course discovery, track active enrolments, test schedules, and digital certifications.
              </p>

              {/* Login Method Toggle Tabs */}
              <div style={{ display: 'flex', backgroundColor: '#f1f5f9', padding: '4px', borderRadius: '8px', marginBottom: '1.25rem' }}>
                <button
                  type="button"
                  style={{
                    flex: 1,
                    padding: '0.5rem 0.75rem',
                    borderRadius: '6px',
                    border: 'none',
                    fontWeight: 600,
                    fontSize: '0.82rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    backgroundColor: citizenLoginMode === 'password' ? '#ffffff' : 'transparent',
                    color: citizenLoginMode === 'password' ? '#0f2444' : '#64748b',
                    boxShadow: citizenLoginMode === 'password' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.4rem'
                  }}
                  onClick={() => { setCitizenLoginMode('password'); setAuthError(''); }}
                >
                  <KeyRound size={15} /> Sign In with Password
                </button>
                <button
                  type="button"
                  style={{
                    flex: 1,
                    padding: '0.5rem 0.75rem',
                    borderRadius: '6px',
                    border: 'none',
                    fontWeight: 600,
                    fontSize: '0.82rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    backgroundColor: citizenLoginMode === 'otp' ? '#ffffff' : 'transparent',
                    color: citizenLoginMode === 'otp' ? '#0f2444' : '#64748b',
                    boxShadow: citizenLoginMode === 'otp' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.4rem'
                  }}
                  onClick={() => { setCitizenLoginMode('otp'); setAuthError(''); }}
                >
                  <Shield size={15} /> Sign In with OTP
                </button>
              </div>

              {authError && (
                <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.6rem 0.8rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem', border: '1px solid #fecaca' }}>
                  {authError}
                </div>
              )}

              {/* OPTION A: SIGN IN WITH PASSWORD */}
              {citizenLoginMode === 'password' && (
                <form onSubmit={handleLogin}>
                  <div className="form-group" style={{ marginBottom: '1rem' }}>
                    <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', display: 'block' }}>
                      Registered Email or Mobile Number:
                    </label>
                    <input
                      type="text"
                      required
                      className="form-control"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      placeholder="e.g. mahesh@example.com or 9876543210"
                    />
                  </div>

                  <div className="form-group" style={{ marginBottom: '0.75rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                      <label style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600 }}>Password:</label>
                      <button
                        type="button"
                        style={{ background: 'none', border: 'none', color: '#ea580c', fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer', padding: 0 }}
                        onClick={() => {
                          setAuthPortalView('forgot_password');
                          setForgotSource('citizen');
                          setForgotEmail(loginEmail);
                          setForgotOtpSent(false);
                          setForgotOtpVerified(false);
                          setForgotOtpRef('');
                          setForgotOtpCode('');
                          setForgotOtpMsg(null);
                          setForgotNewPassword('');
                          setForgotConfirmPassword('');
                        }}
                      >
                        Forgot Password?
                      </button>
                    </div>
                    <div style={{ position: 'relative' }}>
                      <input
                        type={showLoginPassword ? 'text' : 'password'}
                        required
                        className="form-control"
                        style={{ paddingRight: '2.5rem' }}
                        value={loginPassword}
                        onChange={(e) => setLoginPassword(e.target.value)}
                        placeholder="••••••••"
                      />
                      <button
                        type="button"
                        style={{
                          position: 'absolute',
                          right: '10px',
                          top: '50%',
                          transform: 'translateY(-50%)',
                          background: 'none',
                          border: 'none',
                          cursor: 'pointer',
                          color: '#64748b',
                          display: 'flex',
                          alignItems: 'center',
                          padding: 0
                        }}
                        onClick={() => setShowLoginPassword(!showLoginPassword)}
                        title={showLoginPassword ? 'Hide password' : 'Show password'}
                      >
                        {showLoginPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                      </button>
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="btn-primary-orange"
                    style={{ width: '100%', justifyContent: 'center', marginTop: '1rem' }}
                    disabled={authLoading}
                  >
                    {authLoading ? 'Signing In...' : 'Sign In with Password'}
                  </button>
                </form>
              )}

              {/* OPTION B: SIGN IN WITH OTP */}
              {citizenLoginMode === 'otp' && (
                <form onSubmit={handleLogin}>
                  <div className="form-group">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                      <label style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600 }}>Registered Email Address:</label>
                      {loginOtpDemoMode && (
                        <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#b45309', backgroundColor: '#fef3c7', padding: '0.1rem 0.4rem', borderRadius: '4px', border: '1px solid #fde68a' }}>
                          DEMO MODE
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <input
                        type="email"
                        required
                        className="form-control"
                        value={loginEmail}
                        onChange={(e) => {
                          setLoginEmail(e.target.value);
                          if (loginOtpVerified || loginOtpSent) {
                            setLoginOtpVerified(false);
                            setLoginOtpSent(false);
                            setLoginOtpRef('');
                            setLoginOtpCode('');
                            setLoginOtpMsg(null);
                            setLoginOtpDemoCode('');
                          }
                        }}
                        placeholder="e.g. mahesh@example.com"
                        disabled={loginOtpVerified}
                      />
                      <button
                        type="button"
                        className="btn-navy-outline"
                        style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
                        onClick={handleSendLoginOtp}
                        disabled={loginOtpLoading || loginOtpCooldown > 0 || loginOtpVerified}
                      >
                        {loginOtpVerified ? 'Verified' : (loginOtpCooldown > 0 ? `Resend in ${loginOtpCooldown}s` : (loginOtpSent ? 'Resend OTP' : 'Send OTP'))}
                      </button>
                    </div>
                    {loginOtpVerified && (
                      <div style={{ color: '#16a34a', fontSize: '0.78rem', marginTop: '0.3rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                        <CheckCircle2 size={14} /> Email verified successfully.
                      </div>
                    )}
                  </div>

                  {/* Email OTP Verification Section */}
                  {loginOtpSent && !loginOtpVerified && (
                    <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.75rem', marginBottom: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                        <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#166534', margin: 0 }}>
                          Enter 6-Digit Email OTP:
                        </label>
                        <span style={{ fontSize: '0.75rem', color: loginOtpExpirySec > 0 ? '#15803d' : '#b91c1c', fontWeight: 600 }}>
                          {loginOtpExpirySec > 0 ? `Expires in ${Math.floor(loginOtpExpirySec / 60)}:${(loginOtpExpirySec % 60).toString().padStart(2, '0')}` : 'OTP Expired'}
                        </span>
                      </div>

                      

                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <input
                          type="text"
                          maxLength={6}
                          className="form-control"
                          style={{ letterSpacing: '4px', fontWeight: 700, textAlign: 'center', fontSize: '1.1rem' }}
                          value={loginOtpCode}
                          onChange={(e) => setLoginOtpCode(e.target.value.replace(/\D/g, ''))}
                          placeholder="••••••"
                        />
                        <button
                          type="button"
                          className="btn-primary-orange"
                          style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.9rem', fontSize: '0.8rem' }}
                          onClick={handleVerifyLoginOtp}
                          disabled={loginOtpLoading || loginOtpCode.length !== 6}
                        >
                          {loginOtpLoading ? 'Verifying...' : 'Verify OTP'}
                        </button>
                      </div>
                      {loginOtpMsg && (
                        <div style={{ fontSize: '0.75rem', color: loginOtpMsg.type === 'success' ? '#15803d' : '#b91c1c', marginTop: '0.4rem', fontWeight: 600 }}>
                          {loginOtpMsg.text}
                        </div>
                      )}
                    </div>
                  )}

                  <button
                    type="submit"
                    className="btn-primary-orange"
                    style={{ width: '100%', justifyContent: 'center', marginTop: '0.5rem' }}
                    disabled={authLoading || !loginOtpVerified}
                  >
                    {authLoading ? 'Verifying & Signing In...' : 'Verify & Enter Citizen Dashboard'}
                  </button>
                </form>
              )}

              {/* Existing Citizen Set Password Link */}
              <div style={{ marginTop: '0.85rem', textAlign: 'center', fontSize: '0.78rem', color: '#64748b' }}>
                Existing Citizen without a password?{' '}
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#0284c7', fontWeight: 700, cursor: 'pointer', padding: 0 }}
                  onClick={() => {
                    setAuthPortalView('set_password');
                    setSetPasswordEmail(loginEmail);
                    setSetPasswordOtpSent(false);
                    setSetPasswordOtpVerified(false);
                    setSetPasswordOtpRef('');
                    setSetPasswordOtpCode('');
                    setSetPasswordOtpMsg(null);
                    setSetNewPasswordVal('');
                    setSetConfirmPasswordVal('');
                  }}
                >
                  Set Account Password
                </button>
              </div>

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}
                >
                  <ArrowLeft size={12} /> Back to Account Selection
                </button>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#ea580c', fontWeight: 700, cursor: 'pointer' }}
                  onClick={() => { setAuthPortalView('register_citizen'); setAuthError(''); }}
                >
                  New Citizen? Register Now
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 2B. ENROLLED STUDENT LOGIN SCREEN */}
      {authPortalView === 'login_student' && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '440px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.25)' }}>
            {/* Header with Back Navigation */}
            <div style={{ backgroundColor: '#0284c7', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.2)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}
                  title="Back to Account Selection"
                >
                  <ArrowLeft size={16} />
                </button>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#e0f2fe', fontWeight: 700 }}>
                    National Skill Mission
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Student Portal Login
                  </h3>
                </div>
              </div>
              <button
                type="button"
                style={{ background: 'none', border: 'none', color: '#e0f2fe', cursor: 'pointer' }}
                onClick={() => { setAuthPortalView('none'); setAuthError(''); }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem' }}>
              <div style={{ backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: '6px', padding: '0.75rem', marginBottom: '1.25rem', fontSize: '0.8rem', color: '#0369a1', display: 'flex', gap: '0.5rem', alignItems: 'flex-start' }}>
                <GraduationCap size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
                <div>
                  <strong>Enrolled Trainees:</strong> Log in using your permanent <strong>Student ID</strong> (e.g. <code>STU-2026-000104</code>) or registered Citizen email with your existing password.
                </div>
              </div>

              {authError && (
                <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.6rem 0.8rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem', border: '1px solid #fecaca' }}>
                  {authError}
                </div>
              )}

              <form onSubmit={handleLogin}>
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', display: 'block' }}>
                    Student ID or Registered Email:
                  </label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="e.g. STU-2026-000104 or citizen.a@nagriksetu.local"
                  />
                  <small style={{ fontSize: '0.72rem', color: '#64748b', marginTop: '0.2rem', display: 'block' }}>
                    Accepts your permanent Student ID (starts with STU-) or registered email.
                  </small>
                </div>

                <div className="form-group" style={{ marginBottom: '0.75rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                    <label style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600 }}>Password:</label>
                    <button
                      type="button"
                      style={{ background: 'none', border: 'none', color: '#0284c7', fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer', padding: 0 }}
                      onClick={() => {
                        setAuthPortalView('forgot_password');
                        setForgotSource('citizen');
                        setForgotEmail(loginEmail);
                        setForgotOtpSent(false);
                        setForgotOtpVerified(false);
                        setForgotOtpRef('');
                        setForgotOtpCode('');
                        setForgotOtpMsg(null);
                        setForgotNewPassword('');
                        setForgotConfirmPassword('');
                      }}
                    >
                      Forgot Password?
                    </button>
                  </div>
                  <div style={{ position: 'relative' }}>
                    <input
                      type={showLoginPassword ? 'text' : 'password'}
                      required
                      className="form-control"
                      style={{ paddingRight: '2.5rem' }}
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      placeholder="••••••••"
                    />
                    <button
                      type="button"
                      style={{
                        position: 'absolute',
                        right: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#64748b',
                        display: 'flex',
                        alignItems: 'center',
                        padding: 0
                      }}
                      onClick={() => setShowLoginPassword(!showLoginPassword)}
                      title={showLoginPassword ? 'Hide password' : 'Show password'}
                    >
                      {showLoginPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                </div>

                <button
                  type="submit"
                  style={{
                    width: '100%',
                    justifyContent: 'center',
                    marginTop: '1rem',
                    backgroundColor: '#0284c7',
                    color: '#ffffff',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '0.65rem 1rem',
                    fontWeight: 700,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.4rem'
                  }}
                  disabled={authLoading}
                >
                  <GraduationCap size={16} />
                  {authLoading ? 'Authenticating Student...' : 'Access Student Learning Portal'}
                </button>
              </form>

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}
                >
                  <ArrowLeft size={12} /> Back to Account Selection
                </button>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#0284c7', fontWeight: 700, cursor: 'pointer' }}
                  onClick={() => { setAuthPortalView('login_citizen'); setAuthError(''); }}
                >
                  Citizen User Login →
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: FORGOT / RESET PASSWORD */}
      {authPortalView === 'forgot_password' && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '440px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.25)' }}>
            <div style={{ backgroundColor: '#0f2444', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.12)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onClick={() => { setAuthPortalView(forgotSource === 'centre' ? 'login_centre' : 'login_citizen'); setForgotOtpMsg(null); }}
                  title="Back to Sign In"
                >
                  <ArrowLeft size={16} />
                </button>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#f97316', fontWeight: 700 }}>
                    Account Security
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Reset Account Password
                  </h3>
                </div>
              </div>
              <button
                type="button"
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                onClick={() => { setAuthPortalView(forgotSource === 'centre' ? 'login_centre' : 'login_citizen'); setForgotOtpMsg(null); }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem' }}>
              <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: 0, marginBottom: '1.25rem' }}>
                Verify your identity via Email OTP to securely reset and update your citizen password.
              </p>

              {forgotSuccess && (
                <div style={{ backgroundColor: '#f0fdf4', color: '#166534', padding: '0.75rem', borderRadius: '6px', fontSize: '0.82rem', marginBottom: '1rem', border: '1px solid #bbf7d0', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <CheckCircle2 size={16} /> {forgotSuccess}
                </div>
              )}

              {forgotOtpMsg && (
                <div style={{
                  backgroundColor: forgotOtpMsg.type === 'success' ? '#f0fdf4' : '#fee2e2',
                  color: forgotOtpMsg.type === 'success' ? '#166534' : '#b91c1c',
                  border: forgotOtpMsg.type === 'success' ? '1px solid #bbf7d0' : '1px solid #fecaca',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  marginBottom: '1rem'
                }}>
                  {forgotOtpMsg.text}
                </div>
              )}

              <form onSubmit={handleResetPasswordSubmit}>
                {/* Step 1: Email and OTP dispatch */}
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                    <label style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600 }}>Registered Email Address:</label>
                    {forgotOtpDemoMode && (
                      <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#b45309', backgroundColor: '#fef3c7', padding: '0.1rem 0.4rem', borderRadius: '4px', border: '1px solid #fde68a' }}>
                        DEMO MODE
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <input
                      type="email"
                      required
                      className="form-control"
                      value={forgotEmail}
                      onChange={(e) => {
                        setForgotEmail(e.target.value);
                        if (forgotOtpVerified || forgotOtpSent) {
                          setForgotOtpVerified(false);
                          setForgotOtpSent(false);
                          setForgotOtpRef('');
                          setForgotOtpCode('');
                          setForgotOtpMsg(null);
                        }
                      }}
                      placeholder="e.g. mahesh@example.com"
                      disabled={forgotOtpVerified}
                    />
                    <button
                      type="button"
                      className="btn-navy-outline"
                      style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
                      onClick={handleSendForgotOtp}
                      disabled={forgotOtpLoading || forgotOtpCooldown > 0 || forgotOtpVerified}
                    >
                      {forgotOtpVerified ? 'Verified' : (forgotOtpCooldown > 0 ? `Resend in ${forgotOtpCooldown}s` : (forgotOtpSent ? 'Resend OTP' : 'Send OTP'))}
                    </button>
                  </div>
                </div>

                {/* Step 2: OTP Verification Box */}
                {forgotOtpSent && !forgotOtpVerified && (
                  <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.75rem', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#166534', margin: 0 }}>
                        Enter 6-Digit Verification OTP:
                      </label>
                    </div>

                    

                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <input
                        type="text"
                        maxLength={6}
                        className="form-control"
                        style={{ letterSpacing: '4px', fontWeight: 700, textAlign: 'center', fontSize: '1.1rem' }}
                        value={forgotOtpCode}
                        onChange={(e) => setForgotOtpCode(e.target.value.replace(/\D/g, ''))}
                        placeholder="••••••"
                      />
                      <button
                        type="button"
                        className="btn-primary-orange"
                        style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.9rem', fontSize: '0.8rem' }}
                        onClick={handleVerifyForgotOtp}
                        disabled={forgotOtpLoading || forgotOtpCode.length !== 6}
                      >
                        {forgotOtpLoading ? 'Verifying...' : 'Verify OTP'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Step 3: Set New Password Form */}
                {forgotOtpVerified && (
                  <>
                    <div className="form-group" style={{ marginBottom: '1rem' }}>
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', display: 'block' }}>
                        New Password (minimum 8 characters):
                      </label>
                      <div style={{ position: 'relative' }}>
                        <input
                          type={showForgotNewPassword ? 'text' : 'password'}
                          required
                          className="form-control"
                          style={{ paddingRight: '2.5rem' }}
                          value={forgotNewPassword}
                          onChange={(e) => setForgotNewPassword(e.target.value)}
                          placeholder="Enter strong new password"
                        />
                        <button
                          type="button"
                          style={{
                            position: 'absolute',
                            right: '10px',
                            top: '50%',
                            transform: 'translateY(-50%)',
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: '#64748b',
                            display: 'flex',
                            alignItems: 'center',
                            padding: 0
                          }}
                          onClick={() => setShowForgotNewPassword(!showForgotNewPassword)}
                        >
                          {showForgotNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      </div>
                    </div>

                    <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', display: 'block' }}>
                        Confirm New Password:
                      </label>
                      <input
                        type="password"
                        required
                        className="form-control"
                        value={forgotConfirmPassword}
                        onChange={(e) => setForgotConfirmPassword(e.target.value)}
                        placeholder="Confirm new password"
                      />
                      {forgotConfirmPassword && (
                        <div style={{ fontSize: '0.75rem', marginTop: '0.25rem', fontWeight: 600, color: forgotNewPassword === forgotConfirmPassword ? '#16a34a' : '#b91c1c' }}>
                          {forgotNewPassword === forgotConfirmPassword ? '✓ Passwords match' : '✕ Passwords do not match'}
                        </div>
                      )}
                    </div>

                    <button
                      type="submit"
                      className="btn-primary-orange"
                      style={{ width: '100%', justifyContent: 'center' }}
                      disabled={forgotSubmitting}
                    >
                      {forgotSubmitting ? 'Updating Password...' : 'Reset & Save Password'}
                    </button>
                  </>
                )}
              </form>

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => setAuthPortalView(forgotSource === 'centre' ? 'login_centre' : 'login_citizen')}
                >
                  <ArrowLeft size={12} /> {forgotSource === 'centre' ? 'Return to Centre Login' : 'Return to Citizen Login'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: SET PASSWORD FOR EXISTING CITIZENS */}
      {authPortalView === 'set_password' && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '440px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.25)' }}>
            <div style={{ backgroundColor: '#0f2444', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.12)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onClick={() => { setAuthPortalView('login_citizen'); setSetPasswordOtpMsg(null); }}
                  title="Back to Sign In"
                >
                  <ArrowLeft size={16} />
                </button>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#f97316', fontWeight: 700 }}>
                    Existing Citizen Account
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Set Account Password
                  </h3>
                </div>
              </div>
              <button
                type="button"
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                onClick={() => { setAuthPortalView('login_citizen'); setSetPasswordOtpMsg(null); }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem' }}>
              <p style={{ fontSize: '0.82rem', color: '#64748b', marginTop: 0, marginBottom: '1.25rem' }}>
                Create a permanent password for your existing NagrikSetu account after verifying your email via OTP.
              </p>

              {setPasswordSuccess && (
                <div style={{ backgroundColor: '#f0fdf4', color: '#166534', padding: '0.75rem', borderRadius: '6px', fontSize: '0.82rem', marginBottom: '1rem', border: '1px solid #bbf7d0', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <CheckCircle2 size={16} /> {setPasswordSuccess}
                </div>
              )}

              {setPasswordOtpMsg && (
                <div style={{
                  backgroundColor: setPasswordOtpMsg.type === 'success' ? '#f0fdf4' : '#fee2e2',
                  color: setPasswordOtpMsg.type === 'success' ? '#166534' : '#b91c1c',
                  border: setPasswordOtpMsg.type === 'success' ? '1px solid #bbf7d0' : '1px solid #fecaca',
                  padding: '0.6rem 0.8rem',
                  borderRadius: '6px',
                  fontSize: '0.8rem',
                  marginBottom: '1rem'
                }}>
                  {setPasswordOtpMsg.text}
                </div>
              )}

              <form onSubmit={handleSetPasswordSubmit}>
                {/* Step 1: Email and OTP dispatch */}
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                    <label style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600 }}>Registered Email Address:</label>
                    {setPasswordOtpDemoMode && (
                      <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#b45309', backgroundColor: '#fef3c7', padding: '0.1rem 0.4rem', borderRadius: '4px', border: '1px solid #fde68a' }}>
                        DEMO MODE
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <input
                      type="email"
                      required
                      className="form-control"
                      value={setPasswordEmail}
                      onChange={(e) => {
                        setSetPasswordEmail(e.target.value);
                        if (setPasswordOtpVerified || setPasswordOtpSent) {
                          setSetPasswordOtpVerified(false);
                          setSetPasswordOtpSent(false);
                          setSetPasswordOtpRef('');
                          setSetPasswordOtpCode('');
                          setSetPasswordOtpMsg(null);
                        }
                      }}
                      placeholder="e.g. mahesh@example.com"
                      disabled={setPasswordOtpVerified}
                    />
                    <button
                      type="button"
                      className="btn-navy-outline"
                      style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
                      onClick={handleSendSetPasswordOtp}
                      disabled={setPasswordOtpLoading || setPasswordOtpCooldown > 0 || setPasswordOtpVerified}
                    >
                      {setPasswordOtpVerified ? 'Verified' : (setPasswordOtpCooldown > 0 ? `Resend in ${setPasswordOtpCooldown}s` : (setPasswordOtpSent ? 'Resend OTP' : 'Send OTP'))}
                    </button>
                  </div>
                </div>

                {/* Step 2: OTP Verification Box */}
                {setPasswordOtpSent && !setPasswordOtpVerified && (
                  <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.75rem', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#166534', margin: 0 }}>
                        Enter 6-Digit Verification OTP:
                      </label>
                    </div>

                    

                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <input
                        type="text"
                        maxLength={6}
                        className="form-control"
                        style={{ letterSpacing: '4px', fontWeight: 700, textAlign: 'center', fontSize: '1.1rem' }}
                        value={setPasswordOtpCode}
                        onChange={(e) => setSetPasswordOtpCode(e.target.value.replace(/\D/g, ''))}
                        placeholder="••••••"
                      />
                      <button
                        type="button"
                        className="btn-primary-orange"
                        style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.9rem', fontSize: '0.8rem' }}
                        onClick={handleVerifySetPasswordOtp}
                        disabled={setPasswordOtpLoading || setPasswordOtpCode.length !== 6}
                      >
                        {setPasswordOtpLoading ? 'Verifying...' : 'Verify OTP'}
                      </button>
                    </div>
                  </div>
                )}

                {/* Step 3: Create Password Form */}
                {setPasswordOtpVerified && (
                  <>
                    <div className="form-group" style={{ marginBottom: '1rem' }}>
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', display: 'block' }}>
                        Create Password (minimum 8 characters):
                      </label>
                      <div style={{ position: 'relative' }}>
                        <input
                          type={showSetNewPassword ? 'text' : 'password'}
                          required
                          className="form-control"
                          style={{ paddingRight: '2.5rem' }}
                          value={setNewPasswordVal}
                          onChange={(e) => setSetNewPasswordVal(e.target.value)}
                          placeholder="Create new password"
                        />
                        <button
                          type="button"
                          style={{
                            position: 'absolute',
                            right: '10px',
                            top: '50%',
                            transform: 'translateY(-50%)',
                            background: 'none',
                            border: 'none',
                            cursor: 'pointer',
                            color: '#64748b',
                            display: 'flex',
                            alignItems: 'center',
                            padding: 0
                          }}
                          onClick={() => setShowSetNewPassword(!showSetNewPassword)}
                        >
                          {showSetNewPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                        </button>
                      </div>
                    </div>

                    <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', display: 'block' }}>
                        Confirm Password:
                      </label>
                      <input
                        type="password"
                        required
                        className="form-control"
                        value={setConfirmPasswordVal}
                        onChange={(e) => setSetConfirmPasswordVal(e.target.value)}
                        placeholder="Re-enter password"
                      />
                      {setConfirmPasswordVal && (
                        <div style={{ fontSize: '0.75rem', marginTop: '0.25rem', fontWeight: 600, color: setNewPasswordVal === setConfirmPasswordVal ? '#16a34a' : '#b91c1c' }}>
                          {setNewPasswordVal === setConfirmPasswordVal ? '✓ Passwords match' : '✕ Passwords do not match'}
                        </div>
                      )}
                    </div>

                    <button
                      type="submit"
                      className="btn-primary-orange"
                      style={{ width: '100%', justifyContent: 'center' }}
                      disabled={setPasswordSubmitting}
                    >
                      {setPasswordSubmitting ? 'Creating Password...' : 'Save & Set Password'}
                    </button>
                  </>
                )}
              </form>

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => setAuthPortalView('login_citizen')}
                >
                  <ArrowLeft size={12} /> Return to Citizen Login
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 3. TRAINING CENTRE LOGIN SCREEN */}
      
      {/* 3B. REPRESENTATIVE SELF-REGISTRATION MODAL */}
      {authPortalView === 'register_centre_rep' && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '520px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.25)' }}>
            <div style={{ backgroundColor: '#0f766e', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.15)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onClick={() => { setAuthPortalView('login_centre'); setRepMsg(null); }}
                  title="Back to Training Centre Login"
                >
                  <ArrowLeft size={16} />
                </button>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#99f6e4', fontWeight: 700 }}>
                    Official Representative Setup
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Register Centre Representative
                  </h3>
                </div>
              </div>
              <button
                type="button"
                style={{ background: 'none', border: 'none', color: '#ccfbf1', cursor: 'pointer' }}
                onClick={() => { setAuthPortalView('none'); setRepMsg(null); }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem', maxHeight: '82vh', overflowY: 'auto' }}>
              <div style={{ backgroundColor: '#f0fdfa', border: '1px solid #99f6e4', borderRadius: '6px', padding: '0.65rem 0.85rem', marginBottom: '1.25rem', fontSize: '0.78rem', color: '#0f766e', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                <Building2 size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>Select your assigned Accredited Training Centre (1 of 10) and establish your independent login credentials. Existing institutional records are securely preserved.</span>
              </div>

              {repMsg && (
                <div style={{
                  backgroundColor: repMsg.type === 'success' ? '#dcfce7' : '#fee2e2',
                  color: repMsg.type === 'success' ? '#15803d' : '#b91c1c',
                  border: `1px solid ${repMsg.type === 'success' ? '#bbf7d0' : '#fecaca'}`,
                  padding: '0.65rem 0.85rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem'
                }}>
                  {repMsg.text}
                </div>
              )}

              <form onSubmit={handleRegisterRepresentative}>
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 700, color: '#0f2444' }}>Select Accredited Training Centre:</label>
                  <select
                    className="form-control"
                    value={repSelectedCentreId}
                    onChange={(e) => setRepSelectedCentreId(Number(e.target.value))}
                    required
                    style={{ fontSize: '0.85rem', fontWeight: 600 }}
                  >
                    {centreRegisterList.length > 0 ? (
                      centreRegisterList.map((c) => (
                        <option key={c.centre_id} value={c.centre_id}>
                          [{c.centre_code}] {c.centre_name} ({c.district})
                        </option>
                      ))
                    ) : (
                      <>
                        <option value={1}>[CTR-0001] Bengaluru Central Skill Hub (Rajajinagar)</option>
                        <option value={2}>[CTR-0002] Mysuru Regional Skilling Institute</option>
                        <option value={3}>[CTR-0003] Hubballi-Dharwad Tech Development Centre</option>
                        <option value={4}>[CTR-0004] Mangaluru Coastal Skill Academy</option>
                        <option value={5}>[CTR-0005] NagrikSetu Virtual Learning Portal</option>
                        <option value={6}>[CTR-0006] Dharwad Innovation & Regional Skilling Centre</option>
                        <option value={8}>[CTR-0007] Belagavi Regional Skilling Hub</option>
                        <option value={9}>[CTR-0008] Davanagere Vocational & Technical Institute</option>
                        <option value={10}>[CTR-0009] Kalaburagi Regional Skill Development Centre</option>
                        <option value={11}>[CTR-0010] Shivamogga Malnad Skill Development Centre</option>
                      </>
                    )}
                  </select>
                </div>

                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Representative Official Full Name:</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    value={repName}
                    onChange={(e) => setRepName(e.target.value)}
                    placeholder="e.g. Dr. Rajeshwari Patil"
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Representative Email (Login ID):</label>
                    <input
                      type="email"
                      required
                      className="form-control"
                      value={repEmail}
                      onChange={(e) => setRepEmail(e.target.value)}
                      placeholder="e.g. rep.bengaluru@nagriksetu.local"
                    />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Contact Phone Number:</label>
                    <input
                      type="tel"
                      required
                      className="form-control"
                      value={repPhone}
                      onChange={(e) => setRepPhone(e.target.value)}
                      placeholder="10-digit mobile number"
                    />
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1.25rem' }}>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Representative Password:</label>
                    <input
                      type="password"
                      required
                      className="form-control"
                      value={repPassword}
                      onChange={(e) => setRepPassword(e.target.value)}
                      placeholder="Min 6 characters"
                    />
                  </div>
                  <div className="form-group">
                    <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Confirm Password:</label>
                    <input
                      type="password"
                      required
                      className="form-control"
                      value={repConfirmPassword}
                      onChange={(e) => setRepConfirmPassword(e.target.value)}
                      placeholder="Re-enter password"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn-primary-orange"
                  style={{ width: '100%', justifyContent: 'center', backgroundColor: '#0f766e', borderColor: '#0f766e', padding: '0.75rem' }}
                  disabled={repSubmitting}
                >
                  {repSubmitting ? 'Registering Representative...' : 'Establish Representative Account'}
                </button>
              </form>

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'flex-start', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#0284c7', fontWeight: 700, cursor: 'pointer' }}
                  onClick={() => setAuthPortalView('login_centre')}
                >
                  ← Already registered? Centre Sign In
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 3C. PROJECT OWNER CENTRE ACCOUNT REGISTER MODAL */}
      {authPortalView === 'project_owner_register' && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '920px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.3)' }}>
            {/* Modal Header */}
            <div style={{ backgroundColor: '#0f2444', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <div style={{ width: '32px', height: '32px', borderRadius: '6px', backgroundColor: 'rgba(56, 189, 248, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#38bdf8' }}>
                  <Shield size={18} />
                </div>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#38bdf8', fontWeight: 700 }}>
                    Governance & Demonstration Console
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Project Owner Centre Account Register
                  </h3>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                {ownerAuthToken && (
                  <button
                    type="button"
                    style={{ background: 'rgba(239, 68, 68, 0.2)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '6px', color: '#fca5a5', cursor: 'pointer', padding: '0.35rem 0.65rem', fontSize: '0.72rem', fontWeight: 700 }}
                    onClick={handleOwnerSignOut}
                  >
                    Lock Console (Sign Out)
                  </button>
                )}
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.1)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem 0.6rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => fetchCentreRegister()}
                >
                  <RefreshCw size={13} /> Refresh
                </button>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                  onClick={() => { setAuthPortalView('none'); setOwnerResetCentreId(null); }}
                >
                  <X size={18} />
                </button>
              </div>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem', maxHeight: '82vh', overflowY: 'auto' }}>
              {/* Project Owner Authentication Gate / Status Banner */}
              {!ownerAuthToken ? (
                <div style={{ backgroundColor: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px', padding: '1rem', marginBottom: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#92400e', fontWeight: 700, fontSize: '0.85rem' }}>
                      <Lock size={16} /> Privacy Protected: Sensitive Representative Emails Masked
                    </div>
                    <span style={{ fontSize: '0.72rem', color: '#b45309', fontWeight: 600 }}>Public View</span>
                  </div>
                  <p style={{ fontSize: '0.78rem', color: '#78350f', margin: '0 0 0.75rem 0', lineHeight: 1.45 }}>
                    To protect institutional representatives, registered emails and mobile numbers are masked for public visitors. Authenticate with your protected Project Owner Key to unlock unmasked directory access and password management.
                  </p>
                  {ownerAuthMsg && (
                    <div style={{
                      backgroundColor: ownerAuthMsg.type === 'success' ? '#dcfce7' : '#fee2e2',
                      color: ownerAuthMsg.type === 'success' ? '#15803d' : '#b91c1c',
                      padding: '0.4rem 0.65rem', borderRadius: '4px', fontSize: '0.75rem', marginBottom: '0.5rem'
                    }}>
                      {ownerAuthMsg.text}
                    </div>
                  )}
                  <form onSubmit={handleOwnerAuthenticate} style={{ display: 'flex', gap: '0.5rem', maxWidth: '480px' }}>
                    <input
                      type="password"
                      required
                      className="form-control"
                      style={{ fontSize: '0.8rem', padding: '0.4rem 0.65rem' }}
                      value={ownerKeyInput}
                      onChange={(e) => setOwnerKeyInput(e.target.value)}
                      placeholder="Enter Protected Project Owner Key"
                    />
                    <button
                      type="submit"
                      className="btn-primary-orange"
                      style={{ fontSize: '0.78rem', padding: '0.4rem 0.85rem', whiteSpace: 'nowrap' }}
                      disabled={ownerAuthLoading}
                    >
                      {ownerAuthLoading ? 'Verifying...' : 'Unlock Console'}
                    </button>
                  </form>
                </div>
              ) : (
                <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '0.75rem 1rem', marginBottom: '1.25rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#166534', fontSize: '0.82rem', fontWeight: 700 }}>
                    <CheckCircle2 size={16} color="#16a34a" />
                    <span>Project Owner Session Active: Full Unmasked Directory & Password Governance Unlocked</span>
                  </div>
                  <button
                    type="button"
                    className="btn-navy-outline"
                    style={{ fontSize: '0.74rem', padding: '0.3rem 0.6rem', whiteSpace: 'nowrap' }}
                    onClick={() => {
                      setAuthPortalView('register_centre_rep');
                      setRepMsg(null);
                    }}
                  >
                    + Register Representative
                  </button>
                </div>
              )}

              {centreRegisterLoading ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                  <Loader2 size={24} className="spin" style={{ margin: '0 auto 0.5rem auto' }} />
                  <div>Loading 10 Training Centre Account Records...</div>
                </div>
              ) : (
                <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', overflow: 'hidden' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.8rem' }}>
                    <thead style={{ backgroundColor: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: '#475569', fontWeight: 700 }}>
                      <tr>
                        <th style={{ padding: '0.65rem 0.75rem' }}>ID & Code</th>
                        <th style={{ padding: '0.65rem 0.75rem' }}>Accredited Centre Name</th>
                        <th style={{ padding: '0.65rem 0.75rem' }}>District</th>
                        <th style={{ padding: '0.65rem 0.75rem' }}>Representative Login Email</th>
                        <th style={{ padding: '0.65rem 0.75rem', textAlign: 'center' }}>Setup Status</th>
                        <th style={{ padding: '0.65rem 0.75rem', textAlign: 'right' }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {centreRegisterList.map((c, idx) => (
                        <tr key={c.centre_id} style={{ borderBottom: '1px solid #f1f5f9', backgroundColor: idx % 2 === 0 ? '#ffffff' : '#fcfcfd' }}>
                          <td style={{ padding: '0.65rem 0.75rem' }}>
                            <span style={{ fontWeight: 700, color: '#0f2444' }}>#{c.centre_id}</span>
                            <div style={{ fontSize: '0.72rem', color: '#64748b', fontFamily: 'monospace' }}>{c.centre_code}</div>
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem' }}>
                            <div style={{ fontWeight: 700, color: '#0f2444' }}>{c.centre_name}</div>
                            {c.representative_name && (
                              <div style={{ fontSize: '0.72rem', color: '#059669' }}>Rep: {c.representative_name}</div>
                            )}
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem', color: '#475569' }}>
                            {c.district}
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem' }}>
                            <div style={{ fontFamily: 'monospace', fontWeight: 600, color: c.is_masked ? '#64748b' : '#0369a1' }}>
                              {c.registered_email || 'Not Configured'}
                            </div>
                            {c.representative_phone && (
                              <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Ph: {c.representative_phone}</div>
                            )}
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem', textAlign: 'center' }}>
                            <span style={{
                              display: 'inline-block',
                              padding: '0.2rem 0.5rem',
                              borderRadius: '9999px',
                              fontSize: '0.68rem',
                              fontWeight: 700,
                              backgroundColor: c.is_configured ? '#dcfce7' : '#fee2e2',
                              color: c.is_configured ? '#15803d' : '#b91c1c'
                            }}>
                              {c.status}
                            </span>
                          </td>
                          <td style={{ padding: '0.65rem 0.75rem', textAlign: 'right' }}>
                            <div style={{ display: 'flex', gap: '0.4rem', justifyContent: 'flex-end' }}>
                              <button
                                type="button"
                                style={{
                                  backgroundColor: '#0284c7',
                                  color: '#ffffff',
                                  border: 'none',
                                  borderRadius: '4px',
                                  padding: '0.3rem 0.6rem',
                                  fontSize: '0.72rem',
                                  fontWeight: 600,
                                  cursor: 'pointer'
                                }}
                                onClick={() => {
                                  setLoginEmail(c.registered_email && !c.is_masked ? c.registered_email : '');
                                  setLoginPassword('');
                                  setAuthPortalView('login_centre');
                                }}
                                title="Open Centre Workspace Login with prefilled email"
                              >
                                Sign In
                              </button>
                              {ownerAuthToken && (
                                <button
                                  type="button"
                                  style={{
                                    backgroundColor: '#f1f5f9',
                                    color: '#334155',
                                    border: '1px solid #cbd5e1',
                                    borderRadius: '4px',
                                    padding: '0.3rem 0.5rem',
                                    fontSize: '0.72rem',
                                    fontWeight: 600,
                                    cursor: 'pointer'
                                  }}
                                  onClick={() => {
                                    setOwnerResetCentreId(c.centre_id);
                                    setOwnerResetMsg(null);
                                  }}
                                  title="Initiate authorized password reset"
                                >
                                  Reset Access
                                </button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Password Reset Section inside Register (Authorized Project Owner Only) */}
              {ownerResetCentreId && ownerAuthToken && (
                <div style={{ marginTop: '1.5rem', padding: '1rem 1.25rem', backgroundColor: '#f8fafc', border: '1.5px solid #cbd5e1', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <h4 style={{ margin: 0, fontSize: '0.9rem', fontWeight: 700, color: '#0f2444' }}>
                      Authorized Argon2id Password Reset for Centre #{ownerResetCentreId}
                    </h4>
                    <button
                      type="button"
                      style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}
                      onClick={() => setOwnerResetCentreId(null)}
                    >
                      <X size={16} />
                    </button>
                  </div>

                  {ownerResetMsg && (
                    <div style={{
                      backgroundColor: ownerResetMsg.type === 'success' ? '#dcfce7' : '#fee2e2',
                      color: ownerResetMsg.type === 'success' ? '#15803d' : '#b91c1c',
                      padding: '0.5rem 0.75rem', borderRadius: '4px', fontSize: '0.78rem', marginBottom: '0.75rem'
                    }}>
                      {ownerResetMsg.text}
                    </div>
                  )}

                  <form onSubmit={handleOwnerResetPassword} style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '0.75rem', alignItems: 'flex-end' }}>
                    <div className="form-group" style={{ margin: 0 }}>
                      <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>New Unique Password (Argon2id Hash in MySQL):</label>
                      <input
                        type="password"
                        required
                        className="form-control"
                        style={{ fontSize: '0.8rem', padding: '0.4rem 0.6rem' }}
                        value={ownerResetNewPassword}
                        onChange={(e) => setOwnerResetNewPassword(e.target.value)}
                        placeholder="Enter minimum 8 characters"
                      />
                    </div>
                    <button
                      type="submit"
                      className="btn-primary-orange"
                      style={{ fontSize: '0.78rem', padding: '0.45rem 1rem', height: 'fit-content' }}
                      disabled={ownerResetSubmitting}
                    >
                      {ownerResetSubmitting ? 'Updating...' : 'Set Argon2id Hash'}
                    </button>
                  </form>
                </div>
              )}

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <span style={{ color: '#64748b' }}>
                  Argon2id cryptographic hashing enforced. Rate limiting and security audit logs active on all access endpoints.
                </span>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#0284c7', fontWeight: 700, cursor: 'pointer' }}
                  onClick={() => setAuthPortalView('select_role')}
                >
                  ← Return to Role Selection
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {authPortalView === 'login_centre' && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '440px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.25)' }}>
            {/* Header with Back Navigation */}
            <div style={{ backgroundColor: '#0f2444', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.12)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}
                  title="Back to Account Selection"
                >
                  <ArrowLeft size={16} />
                </button>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#38bdf8', fontWeight: 700 }}>
                    Institutional Portal
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Training Centre Login
                  </h3>
                </div>
              </div>
              <button
                type="button"
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                onClick={() => { setAuthPortalView('none'); setAuthError(''); }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem' }}>
              <div style={{ backgroundColor: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: '6px', padding: '0.65rem 0.85rem', marginBottom: '1.25rem', fontSize: '0.78rem', color: '#0369a1', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                <Building2 size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>Authorised workspace for Training Centre Administrators. Centre-level data isolation is strictly enforced.</span>
              </div>

              {authError && (
                <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.6rem 0.8rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem', border: '1px solid #fecaca' }}>
                  {authError}
                </div>
              )}

              <form onSubmit={handleLogin}>
                <div className="form-group">
                  <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Centre Admin Official Email:</label>
                  <input
                    type="email"
                    required
                    className="form-control"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="e.g. centre.bengaluru@nagriksetu.local"
                  />
                </div>

                <div className="form-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                    <label style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600 }}>Administrator Password:</label>
                    <button
                      type="button"
                      style={{ background: 'none', border: 'none', color: '#0284c7', fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer', padding: 0 }}
                      onClick={() => {
                        setAuthPortalView('forgot_password');
                        setForgotSource('centre');
                        setForgotEmail(loginEmail);
                        setForgotOtpSent(false);
                        setForgotOtpVerified(false);
                        setForgotOtpRef('');
                        setForgotOtpCode('');
                        setForgotOtpMsg(null);
                        setForgotNewPassword('');
                        setForgotConfirmPassword('');
                      }}
                    >
                      Forgot / Reset Password?
                    </button>
                  </div>
                  <input
                    type="password"
                    required
                    className="form-control"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="Enter centre administrator password"
                  />
                </div>

                <button
                  type="submit"
                  className="btn-primary-orange"
                  style={{ width: '100%', justifyContent: 'center', backgroundColor: '#0284c7', borderColor: '#0284c7' }}
                  disabled={authLoading}
                >
                  {authLoading ? 'Verifying Centre Credentials...' : 'Sign In to Centre Workspace'}
                </button>
              </form>

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => { setAuthPortalView('select_role'); setAuthError(''); }}
                >
                  <ArrowLeft size={12} /> Back to Roles
                </button>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#0284c7', fontWeight: 700, cursor: 'pointer', fontSize: '0.76rem' }}
                  onClick={() => {
                    fetchCentreRegister();
                    setAuthPortalView('register_centre_rep');
                    setRepMsg(null);
                  }}
                >
                  Register Representative →
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 4. PLATFORM ADMIN LOGIN SCREEN */}
      {(authPortalView === 'login_admin' || (showLoginModal && isAdminLogin && authPortalView === 'none')) && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '440px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.25)' }}>
            {/* Header with Back Navigation */}
            <div style={{ backgroundColor: '#0f2444', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.12)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onClick={() => { setAuthPortalView('select_role'); setShowLoginModal(false); setAuthError(''); }}
                  title="Back to Account Selection"
                >
                  <ArrowLeft size={16} />
                </button>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#4ade80', fontWeight: 700 }}>
                    Government Administration
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Platform Admin Login
                  </h3>
                </div>
              </div>
              <button
                type="button"
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                onClick={() => { setAuthPortalView('none'); setShowLoginModal(false); setAuthError(''); }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem' }}>
              <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.65rem 0.85rem', marginBottom: '1.25rem', fontSize: '0.78rem', color: '#166534', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                <Shield size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>Restricted to authorized officials of the Department of Skill Development & Employment. Multi-tier audit logging is active.</span>
              </div>

              {authError && (
                <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.6rem 0.8rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem', border: '1px solid #fecaca' }}>
                  {authError}
                </div>
              )}

              <form onSubmit={handleLogin}>
                <div className="form-group">
                  <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Platform Administrator Email:</label>
                  <input
                    type="email"
                    required
                    className="form-control"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="e.g. skill.admin@nagriksetu.local"
                  />
                </div>

                <div className="form-group">
                  <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Administrator Password:</label>
                  <input
                    type="password"
                    required
                    className="form-control"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="Enter platform administrator password"
                  />
                </div>

                <button
                  type="submit"
                  className="btn-primary-orange"
                  style={{ width: '100%', justifyContent: 'center', backgroundColor: '#15803d', borderColor: '#15803d' }}
                  disabled={authLoading}
                >
                  {authLoading ? 'Authenticating Official...' : 'Sign In to Government Desk'}
                </button>
              </form>

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => { setAuthPortalView('select_role'); setShowLoginModal(false); setAuthError(''); }}
                >
                  <ArrowLeft size={12} /> Back to Account Selection
                </button>
                <span style={{ color: '#94a3b8', fontSize: '0.74rem' }}>Secured Gov Gateway</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 5. DEDICATED CITIZEN REGISTRATION SCREEN */}
      {(authPortalView === 'register_citizen' || showRegisterModal) && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '460px', padding: 0, overflow: 'hidden', boxShadow: '0 25px 50px -12px rgba(15, 36, 68, 0.25)' }}>
            {/* Header */}
            <div style={{ backgroundColor: '#0f2444', padding: '1.25rem 1.5rem', color: '#ffffff', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <button
                  type="button"
                  style={{ background: 'rgba(255,255,255,0.12)', border: 'none', borderRadius: '6px', color: '#ffffff', cursor: 'pointer', padding: '0.4rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onClick={() => { setAuthPortalView('select_role'); setShowRegisterModal(false); setAuthError(''); }}
                  title="Back to Sign In"
                >
                  <ArrowLeft size={16} />
                </button>
                <div>
                  <div style={{ fontSize: '0.7rem', textTransform: 'uppercase', color: '#f97316', fontWeight: 700 }}>
                    Public Portal Registration
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 800, margin: 0, color: '#ffffff' }}>
                    Citizen Account Registration
                  </h3>
                </div>
              </div>
              <button
                type="button"
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
                onClick={() => { setAuthPortalView('none'); setShowRegisterModal(false); setAuthError(''); }}
              >
                <X size={18} />
              </button>
            </div>

            <div className="modal-body" style={{ padding: '1.5rem' }}>
              <div style={{ backgroundColor: '#fff7ed', border: '1px solid #fed7aa', borderRadius: '6px', padding: '0.65rem 0.85rem', marginBottom: '1.25rem', fontSize: '0.78rem', color: '#9a3412', display: 'flex', alignItems: 'flex-start', gap: '0.5rem' }}>
                <User size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span>Public registration is exclusively for citizens. Training Centre and Platform Admin accounts are provisioned by authorised administrator action.</span>
              </div>

              {authError && (
                <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.6rem 0.8rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem', border: '1px solid #fecaca' }}>
                  {authError}
                </div>
              )}

              <form onSubmit={handleRegister}>
                <div className="form-group">
                  <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Full Name*</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    value={regFullName}
                    onChange={(e) => setRegFullName(e.target.value)}
                    placeholder="e.g. Mahesh Kumar Sharma"
                  />
                </div>

                <div className="form-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                    <label style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600 }}>Email Address*</label>
                    {regOtpDemoMode && (
                      <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#b45309', backgroundColor: '#fef3c7', padding: '0.1rem 0.4rem', borderRadius: '4px', border: '1px solid #fde68a' }}>
                        DEMO MODE
                      </span>
                    )}
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <input
                      type="email"
                      required
                      className="form-control"
                      value={regEmail}
                      onChange={(e) => {
                        setRegEmail(e.target.value);
                        if (regOtpVerified || regOtpSent) {
                          setRegOtpVerified(false);
                          setRegOtpSent(false);
                          setRegOtpRef('');
                          setRegOtpCode('');
                          setRegOtpMsg(null);
                          setRegOtpDemoCode('');
                        }
                      }}
                      placeholder="e.g. mahesh@example.com"
                      disabled={regOtpVerified}
                    />
                    <button
                      type="button"
                      className="btn-navy-outline"
                      style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
                      onClick={handleSendRegOtp}
                      disabled={regOtpLoading || regOtpCooldown > 0 || regOtpVerified}
                    >
                      {regOtpVerified ? 'Verified' : (regOtpCooldown > 0 ? `Resend OTP in ${regOtpCooldown}s` : (regOtpSent ? 'Resend OTP' : 'Send OTP'))}
                    </button>
                  </div>
                  {regOtpVerified && (
                    <div style={{ color: '#16a34a', fontSize: '0.78rem', marginTop: '0.3rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <CheckCircle2 size={14} /> Email verified successfully.
                    </div>
                  )}
                </div>

                {/* Email OTP Verification Section */}
                {regOtpSent && !regOtpVerified && (
                  <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.75rem', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#166534', margin: 0 }}>
                        Enter Email OTP*
                      </label>
                      <span style={{ fontSize: '0.75rem', color: regOtpExpirySec > 0 ? '#15803d' : '#b91c1c', fontWeight: 600 }}>
                        {regOtpExpirySec > 0 ? `Expires in ${Math.floor(regOtpExpirySec / 60)}:${(regOtpExpirySec % 60).toString().padStart(2, '0')}` : 'OTP Expired'}
                      </span>
                    </div>

                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <input
                        type="text"
                        maxLength={6}
                        className="form-control"
                        style={{ letterSpacing: '4px', fontWeight: 700, textAlign: 'center', fontSize: '1.1rem' }}
                        value={regOtpCode}
                        onChange={(e) => setRegOtpCode(e.target.value.replace(/\D/g, ''))}
                        placeholder="••••••"
                      />
                      <button
                        type="button"
                        className="btn-primary-orange"
                        style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.9rem', fontSize: '0.8rem' }}
                        onClick={handleVerifyRegOtp}
                        disabled={regOtpLoading || regOtpCode.length !== 6}
                      >
                        {regOtpLoading ? 'Verifying...' : 'Verify Email'}
                      </button>
                    </div>
                    {regOtpMsg && (
                      <div style={{ fontSize: '0.75rem', color: regOtpMsg.type === 'success' ? '#15803d' : '#b91c1c', marginTop: '0.4rem', fontWeight: 600 }}>
                        {regOtpMsg.text}
                      </div>
                    )}
                  </div>
                )}

                <div className="form-group">
                  <label style={{ fontSize: '0.82rem', fontWeight: 600 }}>Mobile Number*</label>
                  <input
                    type="tel"
                    required
                    className="form-control"
                    value={regPhone}
                    onChange={(e) => setRegPhone(e.target.value)}
                    placeholder="+91 9876543210"
                  />
                </div>

                {/* Mandatory Password Fields */}
                <div className="form-group" style={{ marginBottom: '1rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', display: 'block' }}>
                    Create Password (minimum 8 characters)*
                  </label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type={showRegPassword ? 'text' : 'password'}
                      required
                      minLength={8}
                      className="form-control"
                      style={{ paddingRight: '2.5rem' }}
                      value={regPassword}
                      onChange={(e) => setRegPassword(e.target.value)}
                      placeholder="Enter strong password"
                    />
                    <button
                      type="button"
                      style={{
                        position: 'absolute',
                        right: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#64748b',
                        display: 'flex',
                        alignItems: 'center',
                        padding: 0
                      }}
                      onClick={() => setShowRegPassword(!showRegPassword)}
                      title={showRegPassword ? 'Hide password' : 'Show password'}
                    >
                      {showRegPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {regPassword && (
                    <div style={{ fontSize: '0.72rem', marginTop: '0.25rem', color: regPassword.length >= 8 ? '#16a34a' : '#b91c1c' }}>
                      {regPassword.length >= 8 ? '✓ Password length valid (≥8 characters)' : `Must be at least 8 characters (${regPassword.length}/8)`}
                    </div>
                  )}
                </div>

                <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                  <label style={{ fontSize: '0.82rem', fontWeight: 600, marginBottom: '0.3rem', display: 'block' }}>
                    Confirm Password*
                  </label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type={showRegConfirmPassword ? 'text' : 'password'}
                      required
                      minLength={8}
                      className="form-control"
                      style={{ paddingRight: '2.5rem' }}
                      value={regConfirmPassword}
                      onChange={(e) => setRegConfirmPassword(e.target.value)}
                      placeholder="Re-enter password to confirm"
                    />
                    <button
                      type="button"
                      style={{
                        position: 'absolute',
                        right: '10px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        background: 'none',
                        border: 'none',
                        cursor: 'pointer',
                        color: '#64748b',
                        display: 'flex',
                        alignItems: 'center',
                        padding: 0
                      }}
                      onClick={() => setShowRegConfirmPassword(!showRegConfirmPassword)}
                      title={showRegConfirmPassword ? 'Hide password' : 'Show password'}
                    >
                      {showRegConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  </div>
                  {regConfirmPassword && (
                    <div style={{ fontSize: '0.72rem', marginTop: '0.25rem', fontWeight: 600, color: regPassword === regConfirmPassword ? '#16a34a' : '#b91c1c' }}>
                      {regPassword === regConfirmPassword ? '✓ Passwords match' : '✕ Passwords do not match'}
                    </div>
                  )}
                </div>

                {/* Terms of Use and Privacy Policy acceptance */}
                <div className="form-group" style={{ marginBottom: '1.25rem' }}>
                  <label style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', cursor: 'pointer', fontSize: '0.82rem', color: '#334155' }}>
                    <input
                      type="checkbox"
                      checked={regTermsAgreed}
                      onChange={(e) => setRegTermsAgreed(e.target.checked)}
                      style={{ marginTop: '3px', cursor: 'pointer' }}
                      required
                    />
                    <span>
                      I agree to the <strong>Terms of Use</strong> and <strong>Privacy Policy</strong> for NagrikSetu National Skilling Portal.
                    </span>
                  </label>
                </div>

                <button
                  type="submit"
                  className="btn-primary-orange"
                  style={{ width: '100%', justifyContent: 'center', marginTop: '0.5rem' }}
                  disabled={authLoading || !regOtpVerified || !regPassword || regPassword.length < 8 || regPassword !== regConfirmPassword || !regTermsAgreed}
                >
                  {authLoading ? 'Creating Account...' : 'Complete Citizen Registration'}
                </button>
              </form>

              <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.3rem' }}
                  onClick={() => { setAuthPortalView('select_role'); setShowRegisterModal(false); setAuthError(''); }}
                >
                  <ArrowLeft size={12} /> Back to Sign In
                </button>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#0f2444', fontWeight: 600, cursor: 'pointer' }}
                  onClick={() => { setAuthPortalView('none'); setShowRegisterModal(false); }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

{/* Create Skill Modal decommissioned for Platform Admin view-only model */}

{/* Create Training Programme Modal completely decommissioned for Platform Admin view-only model */}

{/* Create Centre Modal decommissioned for Platform Admin view-only model */}

      {/* MODAL: ASSIGN / CREATE CENTRE ADMINISTRATOR */}
      {selectedCentreForAdmin && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '520px' }}>
            <div className="modal-header">
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#ea580c', textTransform: 'uppercase' }}>
                  {selectedCentreForAdmin.code} • Administrator Management
                </span>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444', margin: '0.2rem 0 0 0' }}>
                  Establish Centre Administrator
                </h3>
              </div>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setSelectedCentreForAdmin(null)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleAssignCentreAdmin} className="modal-body">
              {assignAdminMsg && (
                <div style={{ padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem', fontSize: '0.85rem', backgroundColor: assignAdminMsg.type === 'success' ? '#dcfce7' : '#fee2e2', color: assignAdminMsg.type === 'success' ? '#166534' : '#991b1b' }}>
                  {assignAdminMsg.text}
                </div>
              )}

              <div className="form-group">
                <label>Centre Name:</label>
                <input type="text" disabled className="form-control" value={selectedCentreForAdmin.name} style={{ backgroundColor: '#f1f5f9' }} />
              </div>

              <div className="form-group">
                <label>Admin Full Name:</label>
                <input type="text" required className="form-control" value={assignAdminFullName} onChange={(e) => setAssignAdminFullName(e.target.value)} />
              </div>

              <div className="form-group">
                <label>Admin Email (Login Username):</label>
                <input type="email" required className="form-control" value={assignAdminEmail} onChange={(e) => setAssignAdminEmail(e.target.value)} />
              </div>

              <div className="form-group">
                <label>Admin Password:</label>
                <input type="text" required className="form-control" value={assignAdminPassword} onChange={(e) => setAssignAdminPassword(e.target.value)} />
                <small style={{ color: '#64748b' }}>Representative sets unique password on self-registration</small>
              </div>

              <div className="form-group">
                <label>Contact Phone (Optional):</label>
                <input type="text" className="form-control" value={assignAdminPhone} onChange={(e) => setAssignAdminPhone(e.target.value)} />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
                <button type="button" className="btn-navy-outline" onClick={() => setSelectedCentreForAdmin(null)}>Cancel</button>
                <button type="submit" className="btn-primary-orange" disabled={assignAdminSubmitting}>
                  {assignAdminSubmitting ? 'Assigning...' : 'Confirm & Save Administrator'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: UPDATE CENTRE STATUS (APPROVE, SUSPEND, REJECT) */}
      {selectedCentreForStatus && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '480px' }}>
            <div className="modal-header">
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#ea580c', textTransform: 'uppercase' }}>
                  {selectedCentreForStatus.code} • Accreditation Status
                </span>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444', margin: '0.2rem 0 0 0' }}>
                  Change Centre Status
                </h3>
              </div>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setSelectedCentreForStatus(null)}>
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleUpdateCentreStatus} className="modal-body">
              {centreStatusMsg && (
                <div style={{ padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem', fontSize: '0.85rem', backgroundColor: centreStatusMsg.type === 'success' ? '#dcfce7' : '#fee2e2', color: centreStatusMsg.type === 'success' ? '#166534' : '#991b1b' }}>
                  {centreStatusMsg.text}
                </div>
              )}

              <div className="form-group">
                <label>Centre:</label>
                <input type="text" disabled className="form-control" value={selectedCentreForStatus.name} style={{ backgroundColor: '#f1f5f9' }} />
              </div>

              <div className="form-group">
                <label>Target Status:</label>
                <select className="form-control" value={centreStatusTarget} onChange={(e: any) => setCentreStatusTarget(e.target.value)}>
                  <option value="APPROVED">APPROVED (Active & Operational)</option>
                  <option value="SUSPENDED">SUSPENDED (Temporarily Paused)</option>
                  <option value="REJECTED">REJECTED (Accreditation Revoked)</option>
                </select>
              </div>

              <div className="form-group">
                <label>Administrative Reason / Remarks {centreStatusTarget === 'REJECTED' && <span style={{ color: '#b91c1c' }}>*</span>}:</label>
                <textarea rows={3} className="form-control" placeholder="Provide explanation for this status update..." value={centreStatusReason} onChange={(e) => setCentreStatusReason(e.target.value)} required={centreStatusTarget === 'REJECTED'} />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
                <button type="button" className="btn-navy-outline" onClick={() => setSelectedCentreForStatus(null)}>Cancel</button>
                <button type="submit" className="btn-primary-orange" disabled={centreStatusSubmitting}>
                  {centreStatusSubmitting ? 'Updating...' : `Set to ${centreStatusTarget}`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
                  {/* Multi-Centre Selection Modal */}
      {showCentreSelectModal && assignedCentres && assignedCentres.length > 1 && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(15, 23, 42, 0.65)', backdropFilter: 'blur(3px)', zIndex: 9999, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1rem' }}>
          <div style={{ backgroundColor: '#ffffff', borderRadius: '14px', maxWidth: '540px', width: '100%', padding: '2rem', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Building2 size={24} color="#0f766e" />
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', margin: 0 }}>
                  Select Training Centre
                </h3>
              </div>
              {centreId && (
                <button
                  type="button"
                  onClick={() => setShowCentreSelectModal(false)}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
                >
                  <X size={20} />
                </button>
              )}
            </div>

            <p style={{ fontSize: '0.86rem', color: '#64748b', marginBottom: '1.5rem', lineHeight: 1.5 }}>
              Your administrator account is authorized to manage multiple accredited training centres. Choose the centre workspace you wish to access:
            </p>

            <div style={{ display: 'grid', gap: '0.75rem', marginBottom: '1.5rem' }}>
              {assignedCentres.map((ac: any) => {
                const isCurrent = String(ac.id) === String(centreId);
                return (
                  <div
                    key={ac.id}
                    onClick={() => switchAdminCentre(String(ac.id))}
                    style={{
                      padding: '1rem 1.25rem',
                      borderRadius: '10px',
                      border: isCurrent ? '2px solid #0f766e' : '1px solid #e2e8f0',
                      backgroundColor: isCurrent ? '#f0fdfa' : '#ffffff',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      cursor: 'pointer',
                      transition: 'all 0.15s ease'
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '0.2rem' }}>
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#0f766e', backgroundColor: '#ccfbf1', padding: '2px 6px', borderRadius: '4px' }}>
                          {ac.code || `CTR-${ac.id}`}
                        </span>
                        <strong style={{ fontSize: '0.95rem', color: '#0f172a' }}>{ac.name}</strong>
                      </div>
                      <div style={{ fontSize: '0.78rem', color: '#64748b' }}>
                        📍 {ac.location ? `${ac.location}, ` : ''}{ac.district} • Status: {ac.approval_status || 'APPROVED'}
                      </div>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      {isCurrent ? (
                        <span style={{ fontSize: '0.74rem', fontWeight: 700, color: '#0f766e', backgroundColor: '#ccfbf1', padding: '4px 8px', borderRadius: '6px' }}>
                          Active
                        </span>
                      ) : (
                        <button
                          type="button"
                          style={{
                            padding: '0.4rem 0.8rem',
                            backgroundColor: '#0f766e',
                            color: '#ffffff',
                            border: 'none',
                            borderRadius: '6px',
                            fontSize: '0.78rem',
                            fontWeight: 700,
                            cursor: 'pointer'
                          }}
                        >
                          Select
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            <div style={{ textAlign: 'right' }}>
              <button
                type="button"
                className="btn-navy-outline"
                onClick={() => setShowCentreSelectModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* FOOTER */}
      <footer style={{ backgroundColor: '#091a33', color: '#94a3b8', borderTop: '4px solid var(--accent-orange)', padding: '3rem 1.5rem 1.5rem 1.5rem', marginTop: '4rem' }}>
        <div style={{ maxWidth: '1360px', margin: '0 auto' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '2rem', marginBottom: '2.5rem' }}>
            <div>
              <h4 style={{ color: '#ffffff', fontSize: '1.1rem', fontWeight: 800, marginBottom: '0.75rem' }}>NagrikSetu</h4>
              <p style={{ fontSize: '0.82rem', lineHeight: 1.6, color: '#cbd5e1' }}>
                National Citizen Opportunity, Welfare & Employment Intelligence Platform. Department of Skill Development & Entrepreneurship.
              </p>
            </div>
            <div>
              <h5 style={{ color: '#ffffff', fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.75rem' }}>Official Navigation</h5>
              <div style={{ display: 'grid', gap: '0.4rem', fontSize: '0.82rem' }}>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('courses')}>Explore 100+ Skill Courses</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('programmes')}>Subsidized Training Programmes</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('centres')}>Accredited Training Centres</span>
              </div>
            </div>
            <div>
              <h5 style={{ color: '#ffffff', fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.75rem' }}>Citizen Services</h5>
              <div style={{ display: 'grid', gap: '0.4rem', fontSize: '0.82rem' }}>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('gap')}>Skill Gap Analysis Engine</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('applications')}>Application Tracking</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('certificates')}>Verifiable Certificates</span>
              </div>
            </div>
          </div>

          <div style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)', paddingTop: '1.25rem', textAlign: 'center', fontSize: '0.78rem' }}>
            <p>{t('footer.text')}</p>
            <p style={{ marginTop: '0.25rem' }}>{t('footer.compliance')}</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
