import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import i18n from './i18n';
import {
  Landmark, BookOpen, GraduationCap, Users, Target, HeartHandshake,
  CheckCircle2, ArrowRight, Menu, LogOut, LogIn, UserPlus, Search, Globe,
  Building2, Award, Clock, AlertCircle, FileText, Briefcase, Filter,
  Shield, Check, X, ChevronRight, Calendar, User, MapPin, Download, RefreshCw,
  Send, Folder, Bookmark, BookmarkCheck, Navigation, Crosshair, Compass, Loader2, Star, Sparkles
} from 'lucide-react';
import './style.css';
import { CentreLocationMap } from './CentreLocationMap';

const API_BASE = import.meta.env.VITE_SKILL_API_URL || (window.location.port === '5173' && window.location.hostname !== 'localhost' ? '' : 'http://localhost:8003');

export default function App() {
  const { t } = useTranslation();

  // Navigation & Page State
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [adminMobileMenuOpen, setAdminMobileMenuOpen] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'home' | 'courses' | 'programmes' | 'trainers' | 'centres' | 'careers' | 'applications' | 'profile' | 'gap' | 'certificates'>('home');

  // Authentication State
  const [token, setToken] = useState<string>(localStorage.getItem('ns_skill_token') || '');
  const [userRole, setUserRole] = useState<string>(localStorage.getItem('ns_skill_role') || '');
  const [citizenRef, setCitizenRef] = useState<string>(localStorage.getItem('ns_skill_citizen_ref') || '');
  const [userEmail, setUserEmail] = useState<string>(localStorage.getItem('ns_skill_email') || '');
  const [userName, setUserName] = useState<string>(localStorage.getItem('ns_skill_name') || '');

  // Auth Modals
  const [showLoginModal, setShowLoginModal] = useState<boolean>(false);
  const [showRegisterModal, setShowRegisterModal] = useState<boolean>(false);
  const [authError, setAuthError] = useState<string>('');
  const [authLoading, setAuthLoading] = useState<boolean>(false);

  // Form Inputs for Auth
  const [loginEmail, setLoginEmail] = useState<string>('');
  const [loginPassword, setLoginPassword] = useState<string>('');
  const [isAdminLogin, setIsAdminLogin] = useState<boolean>(false);
  const [loginMethod, setLoginMethod] = useState<'password' | 'otp'>('password');
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
  const [categories, setCategories] = useState<any[]>([]);
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
  const [adminTab, setAdminTab] = useState<'applications' | 'skills' | 'programmes' | 'centres'>('applications');
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

    fetch(`${API_BASE}/api/centres/search?location=${encodeURIComponent(query)}&radius_km=${parsedRadius}`)
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

          {/* Facilities / Details */}
          {c.facilities && (
            <div style={{ backgroundColor: '#f8fafc', padding: '0.65rem', borderRadius: '6px', fontSize: '0.76rem', color: '#334155', marginBottom: '0.65rem', lineHeight: '1.4' }}>
              <strong style={{ color: '#0f172a' }}>Facilities:</strong> {c.facilities}
            </div>
          )}

          {/* Contact details */}
          <div style={{ fontSize: '0.78rem', color: '#64748b', lineHeight: '1.5' }}>
            {c.phone && <div><strong>Contact:</strong> {c.phone}</div>}
            {c.website && (
              <div>
                <strong>Website:</strong>{' '}
                <a href={c.website} target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb', textDecoration: 'none' }}>
                  {c.website.replace('https://', '').replace('http://', '').slice(0, 30)}
                </a>
              </div>
            )}
          </div>
        </div>

        {/* Bottom Action Button: View on Map */}
        <div style={{ marginTop: '1.25rem', borderTop: '1px solid #f1f5f9', paddingTop: '1rem' }}>
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
              width: '100%',
              boxSizing: 'border-box',
              backgroundColor: isSelected ? '#1e3a8a' : '#ea580c',
              color: '#ffffff',
              border: 'none',
              textAlign: 'center',
              padding: '0.65rem 1rem',
              borderRadius: '6px',
              fontSize: '0.85rem',
              fontWeight: 600,
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.45rem',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            <MapPin size={15} /> {isSelected ? 'Focused on Map' : 'View on Map'}
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
    }
  }, [token, userRole]);


  // Save or Unsave Career Opportunity permanently
  const handleToggleSaveJob = async (job: any) => {
    if (!token) {
      setShowLoginModal(true);
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
      setShowLoginModal(true);
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
        setLoginOtpCode(data.demo_otp);
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

  // Handle Citizen & Admin Login
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    const isUsingPassword = isAdminLogin || loginMethod === 'password' || Boolean(loginPassword.trim() && !loginOtpVerified);
    if (!isUsingPassword && (!loginOtpVerified || !loginOtpRef)) {
      setAuthError('Please verify your email address via OTP before logging in, or enter your password.');
      return;
    }
    setAuthLoading(true);
    setAuthError('');
    try {
      const payload: any = { email: loginEmail.trim() };
      if (isUsingPassword) {
        if (!loginPassword.trim()) {
          throw new Error('Please enter your account password.');
        }
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

      setToken(data.access_token);
      setUserRole(data.role);
      setCitizenRef(data.citizen_ref || '');
      setUserEmail(data.email);
      setUserName(data.full_name || '');

      localStorage.setItem('ns_skill_token', data.access_token);
      localStorage.setItem('ns_skill_role', data.role);
      localStorage.setItem('ns_skill_citizen_ref', data.citizen_ref || '');
      localStorage.setItem('ns_skill_email', data.email);
      localStorage.setItem('ns_skill_name', data.full_name || '');

      setShowLoginModal(false);
      setBannerNotice(`Welcome back, ${data.full_name || data.email}!`);
      if (data.role === 'SKILL_DEPARTMENT_ADMIN') {
        setAdminTab('applications');
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
        setRegOtpCode(data.demo_otp);
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
    if (!regPassword || regPassword.trim().length < 6) {
      setAuthError('Please choose a password with at least 6 characters.');
      return;
    }
    setAuthLoading(true);
    setAuthError('');
    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          full_name: regFullName.trim(),
          email: regEmail.trim(),
          phone: regPhone.trim(),
          password: regPassword.trim(),
          otp_reference: regOtpRef
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Registration failed');

      // Pre-fill registered email and password for smooth login
      setLoginEmail(regEmail.trim());
      setLoginPassword(regPassword.trim());
      setLoginMethod('password');

      // Navigate to login
      setShowRegisterModal(false);
      setShowLoginModal(true);
      setBannerNotice('Account created successfully! Your credentials have been pre-filled. Click Login below.');
    } catch (err: any) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    setToken('');
    setUserRole('');
    setCitizenRef('');
    setUserEmail('');
    setUserName('');
    localStorage.removeItem('ns_skill_token');
    localStorage.removeItem('ns_skill_role');
    localStorage.removeItem('ns_skill_citizen_ref');
    localStorage.removeItem('ns_skill_email');
    localStorage.removeItem('ns_skill_name');
    setActiveTab('home');
    setBannerNotice('You have been signed out.');
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
  const handleStartEnrolment = (prog: any) => {
    setEnrollingProgram(prog);
    setSelectedBatchId(prog.batches && prog.batches.length > 0 ? prog.batches[0].id : null);
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
    setAppPrefMode(prog.delivery_mode || 'Hybrid');

    setEnrolmentStatement(myProfile?.career_goals || 'I am eager to master this curriculum to qualify for industry software engineering certifications and secure high-impact roles.');
    setAppTargetSkills(prog.skill?.name || prog.title || '');
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
    if (!token) {
      setShowLoginModal(true);
      return;
    }
    if (!enrolOtpVerified || !enrolOtpRef) {
      setEnrolmentErrorMsg('Mobile OTP verification is required before submitting your application.');
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
      const comprehensiveDossier = {
        section_a_personal: {
          full_name: appFullName,
          email: appEmail,
          phone: appPhone,
          date_of_birth: appDob,
          gender: appGender,
          alternate_phone: appAltPhone
        },
        section_b_address: {
          residential_address: appAddress,
          city: appCity,
          state: appState,
          pincode: appPincode
        },
        section_c_education: {
          highest_qualification: appEducation,
          institution: appInstitution,
          graduation_year: appGradYear,
          specialization: appSpecialization
        },
        section_d_employment: {
          employment_status: appEmploymentStatus,
          occupation: appOccupation,
          experience_years: appExperienceYears
        },
        section_e_training_preferences: {
          program_title: enrollingProgram.title,
          preferred_mode: appPrefMode,
          preferred_timing: appPrefTiming,
          batch_id: selectedBatchId
        },
        section_f_career_motivation: {
          statement_of_purpose: enrolmentStatement,
          target_skills: appTargetSkills,
          placement_assistance_required: appPostJobPlacement
        },
        section_g_documents: {
          id_proof_type: appIdProofType,
          id_proof_reference: appIdProofNumber,
          locker_verification_note: appDocAttachedNote
        },
        section_h_declaration: {
          agreed: true,
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
          application_details: comprehensiveDossier,
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
    } catch (err: any) {
      alert(err.message);
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
      {/* 0. Indian Flag Tricolor Ribbon */}
      <div style={{ height: '5px', width: '100%', background: 'linear-gradient(to right, #FF9933 0%, #FF9933 33.3%, #FFFFFF 33.3%, #FFFFFF 66.6%, #138808 66.6%, #138808 100%)' }} />

      {/* 1. Official Government Top Utility Bar */}
      <div className="gov-top-bar" style={{ background: '#081c33', color: '#f8fafc', padding: '0.4rem 1.25rem', fontSize: '0.78rem', borderBottom: '1px solid #1e293b' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
          <span style={{ color: '#FF9933', fontWeight: 800 }}>भारत सरकार</span>
          <span style={{ color: '#475467' }}>|</span>
          <span style={{ fontWeight: 600 }}>Government of India</span>
          <span style={{ color: '#475467' }}>|</span>
          <span style={{ color: '#94a3b8' }}>कौशल विकास एवं उद्यमिता सेवा (Skill Development Service · MSDE / Karnataka)</span>
        </div>
        <div style={{ display: 'flex', gap: '0.65rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <a
            href="http://localhost:5173"
            style={{
              background: 'rgba(255, 153, 51, 0.15)',
              color: '#FF9933',
              border: '1px solid rgba(255, 153, 51, 0.4)',
              padding: '0.2rem 0.65rem',
              borderRadius: '6px',
              textDecoration: 'none',
              fontWeight: 700,
              fontSize: '0.75rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.3rem'
            }}
          >
            🏛️ Central Portal (Port 5173)
          </a>
          <a
            href="http://localhost:5174"
            style={{
              background: 'rgba(255, 255, 255, 0.1)',
              color: '#cbd5e1',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              padding: '0.2rem 0.65rem',
              borderRadius: '6px',
              textDecoration: 'none',
              fontWeight: 600,
              fontSize: '0.75rem',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.3rem'
            }}
          >
            🎓 School Service (Port 5174)
          </a>
          <span>Accessibility: WCAG 2.2 AA</span>
          <div style={{ display: 'flex', gap: '0.25rem', marginLeft: '0.25rem' }}>
            <button
              type="button"
              onClick={() => i18n.changeLanguage('en')}
              style={{
                background: i18n.language === 'en' ? '#FF9933' : 'transparent',
                color: i18n.language === 'en' ? '#081c33' : '#cbd5e1',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '4px',
                padding: '0.1rem 0.4rem',
                fontSize: '0.7rem',
                fontWeight: 700
              }}
            >
              EN
            </button>
            <button
              type="button"
              onClick={() => i18n.changeLanguage('kn')}
              style={{
                background: i18n.language === 'kn' ? '#FF9933' : 'transparent',
                color: i18n.language === 'kn' ? '#081c33' : '#cbd5e1',
                border: '1px solid rgba(255,255,255,0.2)',
                borderRadius: '4px',
                padding: '0.1rem 0.4rem',
                fontSize: '0.7rem',
                fontWeight: 700
              }}
            >
              ಕನ್ನಡ
            </button>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* DEDICATED SKILL DEPARTMENT ADMINISTRATOR DESK & WORKSPACE             */}
      {/* Strict separation: Administrators NEVER render Citizen Dashboard       */}
      {/* ========================================================================= */}
      {userRole === 'SKILL_DEPARTMENT_ADMIN' ? (
        <div>
          {/* Dedicated Admin Top Navigation */}
          <header className="header-main" style={{ borderBottom: '3px solid #0f2444', backgroundColor: '#ffffff' }}>
            <div className="header-container">
              <div className="brand-wrapper" onClick={() => { setAdminTab('applications'); setAdminMobileMenuOpen(false); }}>
                <div className="brand-emblem" style={{ background: 'linear-gradient(135deg, #091a33 0%, #1e3a8a 100%)' }}>
                  <Shield size={24} />
                </div>
                <div className="brand-text">
                  <h1 style={{ color: '#081c33', fontWeight: 800 }}>
                    नागरिक सेतु <span style={{ color: '#FF9933' }}>· NagrikSetu</span>
                  </h1>
                  <p style={{ letterSpacing: '0.04em', color: '#081c33', fontWeight: 700 }}>Skill Department Administration Desk</p>
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
          <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', borderBottom: '2px solid #e2e8f0', paddingBottom: '0.5rem' }}>
            <button
              className={`nav-item-btn ${adminTab === 'applications' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('applications')}
            >
              Citizen Applications Queue ({adminEnrollments.length})
            </button>
            <button
              className={`nav-item-btn ${adminTab === 'skills' ? 'active' : ''}`}
              style={{ fontSize: '0.95rem', padding: '0.5rem 1rem' }}
              onClick={() => setAdminTab('skills')}
            >
              Skill Catalogue Management
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
                            setReviewStatus(a.status === 'PENDING' ? 'APPROVED' : a.status);
                            setReviewRemarks(a.admin_remarks || '');
                          }}
                        >
                          Review
                        </button>
                        {a.status === 'APPROVED' && !a.certificate_issued && (
                          <button
                            className="btn-primary-orange"
                            style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                            onClick={() => handleIssueCertificate(a.id)}
                          >
                            Certify
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

          {/* TAB 2: SKILL CATALOGUE MANAGEMENT */}
          {adminTab === 'skills' && (
            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>Skill Catalogue Directory</h3>
                  <p style={{ fontSize: '0.82rem', color: '#64748b' }}>Create, update, and manage official NSQF skilling courses</p>
                </div>
                <button className="btn-primary-orange" onClick={() => setShowAddSkillModal(true)}>
                  + Add New Skill Course
                </button>
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
            </div>
          )}

          {/* TAB 3: TRAINING PROGRAMMES & BATCH CAPACITY */}
          {adminTab === 'programmes' && (
            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>Training Programmes & Concurrency Capacity</h3>
                  <p style={{ fontSize: '0.82rem', color: '#64748b' }}>Configure training offerings, manage available batch seats, and inspect state transitions</p>
                </div>
                <button className="btn-primary-orange" onClick={() => setShowAddProgrammeModal(true)}>
                  + Create Training Programme
                </button>
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
          {adminTab === 'centres' && (
            <div style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a' }}>Accredited Training Centres Management</h3>
                  <p style={{ fontSize: '0.82rem', color: '#64748b' }}>Configure regional centres, computer labs, and smart training facilities</p>
                </div>
                <button className="btn-primary-orange" onClick={() => setShowAddCentreModal(true)}>
                  + Add Training Centre
                </button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
                {centres.map((c: any) => (
                  <div key={c.code} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#f8fafc' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#ea580c' }}>{c.code}</span>
                      <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{c.district}, {c.state}</span>
                    </div>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.4rem' }}>{c.name}</h4>
                    <p style={{ fontSize: '0.8rem', color: '#475569', marginBottom: '0.6rem' }}>{c.address}</p>
                    <div style={{ fontSize: '0.78rem', color: '#64748b' }}>
                      <div><strong>Contact:</strong> {c.contact_phone} • {c.contact_email}</div>
                      <div><strong>Facilities:</strong> {c.facilities}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
          </div>
        </div>
      ) : (
        /* CITIZEN PORTAL & DASHBOARD */
        <div>
          {/* 2. Main Navigation Bar */}
      <header className="header-main">
        <div className="header-container">
          <div className="brand-wrapper" onClick={() => { setActiveTab('home'); setMobileMenuOpen(false); }}>
            <div className="brand-emblem" style={{ background: '#081c33', border: '1px solid #FF9933' }}>
              <Sparkles size={24} style={{ color: '#FF9933' }} />
            </div>
            <div className="brand-text">
              <h1 style={{ color: '#081c33', fontWeight: 800 }}>
                नागरिक सेतु <span style={{ color: '#FF9933' }}>· NagrikSetu</span>
              </h1>
              <p style={{ color: '#475467', fontWeight: 600 }}>ಕೌಶಲ್ಯ ವಿಕಾಸ ಸೇವೆ • Skill Development Service</p>
            </div>
          </div>

          <button
            type="button"
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          <nav className={`nav-links ${mobileMenuOpen ? 'nav-open' : ''}`}>
            <button className={`nav-item-btn ${activeTab === 'home' ? 'active' : ''}`} onClick={() => { setActiveTab('home'); setMobileMenuOpen(false); }}>
              {t('nav.home')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'courses' ? 'active' : ''}`} onClick={() => { setActiveTab('courses'); setMobileMenuOpen(false); }}>
              {t('nav.explore_courses')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'programmes' ? 'active' : ''}`} onClick={() => { setActiveTab('programmes'); setMobileMenuOpen(false); }}>
              {t('nav.training_programmes')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'trainers' ? 'active' : ''}`} onClick={() => { setActiveTab('trainers'); setMobileMenuOpen(false); }}>
              {t('nav.trainers')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'centres' ? 'active' : ''}`} onClick={() => { setActiveTab('centres'); setMobileMenuOpen(false); }}>
              {t('nav.centres')}
            </button>
            <button className={`nav-item-btn ${activeTab === 'careers' ? 'active' : ''}`} onClick={() => { setActiveTab('careers'); setMobileMenuOpen(false); }}>
              {t('nav.careers')}
            </button>

            {token && (
              <>
                <button className={`nav-item-btn ${activeTab === 'applications' ? 'active' : ''}`} onClick={() => { setActiveTab('applications'); setMobileMenuOpen(false); }}>
                  {t('nav.my_applications')} ({myApplications.length})
                </button>
                <button className={`nav-item-btn ${activeTab === 'profile' ? 'active' : ''}`} onClick={() => { setActiveTab('profile'); setMobileMenuOpen(false); }}>
                  {t('nav.my_profile')}
                </button>
                <button className={`nav-item-btn ${activeTab === 'certificates' ? 'active' : ''}`} onClick={() => { setActiveTab('certificates'); setMobileMenuOpen(false); }}>
                  {t('nav.certificates')}
                </button>
              </>
            )}
            <button className={`nav-item-btn ${activeTab === 'gap' ? 'active' : ''}`} onClick={() => { setActiveTab('gap'); setMobileMenuOpen(false); }}>
              {t('nav.gap_analysis')}
            </button>
          </nav>

          <div className="nav-actions">
            {token ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: '#334155' }}>
                  {userName || citizenRef}
                </span>
                {userRole === 'SKILL_DEPARTMENT_ADMIN' && (
                  <button className="btn-admin-pill" onClick={() => setAdminTab('applications')}>
                    <Shield size={14} /> Admin Desk
                  </button>
                )}
                <button className="btn-navy-outline" onClick={handleLogout}>
                  <LogOut size={14} /> {t('nav.logout')}
                </button>
              </div>
            ) : (
              <>
                <button className="btn-navy-outline" onClick={() => setShowLoginModal(true)}>
                  <LogIn size={14} /> {t('nav.sign_in')}
                </button>
                <button className="btn-primary-orange" onClick={() => setShowRegisterModal(true)}>
                  <UserPlus size={14} /> {t('nav.register')}
                </button>
                <button className="btn-admin-pill" onClick={() => { setShowLoginModal(true); setIsAdminLogin(true); setLoginEmail('skill.admin@nagriksetu.local'); setLoginPassword('SkillAdmin@2026!'); }}>
                  <Shield size={14} /> Admin
                </button>
              </>
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
                {t('hero.title')} • <span className="accent">{t('hero.sub_title')}</span>
              </h1>
              <p className="hero-tagline">{t('hero.tagline')}</p>
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

              {/* Hero Stats */}
              <div className="hero-stats-row">
                <div className="hero-stat-card">
                  <div className="hero-stat-number">{totalSkills || 104}+</div>
                  <div className="hero-stat-label">Accredited Skill Tracks</div>
                </div>
                <div className="hero-stat-card">
                  <div className="hero-stat-number">{programmes.length || 104}+</div>
                  <div className="hero-stat-label">Subsidized Batches</div>
                </div>
                <div className="hero-stat-card">
                  <div className="hero-stat-number">{trainers.length || 6}</div>
                  <div className="hero-stat-label">Lead Faculty & Trainers</div>
                </div>
                <div className="hero-stat-card">
                  <div className="hero-stat-number">{centres.length || 5}</div>
                  <div className="hero-stat-label">Regional Training Centres</div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Categories Bar */}
          <div className="main-container">
            <div className="section-header">
              <div>
                <h2>{t('sections.categories')}</h2>
                <p>Select a skilling sector to filter accredited curriculum</p>
              </div>
              <button className="btn-navy-outline" onClick={() => setActiveTab('courses')}>
                View All Courses <ArrowRight size={14} />
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '1rem', marginBottom: '3rem' }}>
              {categories.map((c: any) => (
                <div
                  key={c.code}
                  style={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '8px',
                    padding: '1.25rem',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease'
                  }}
                  onClick={() => {
                    setSelectedCategory(c.name);
                    setActiveTab('courses');
                  }}
                >
                  <div style={{ color: 'var(--accent-orange)', marginBottom: '0.5rem' }}>
                    <BookOpen size={22} />
                  </div>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.35rem' }}>{c.name}</h4>
                  <p style={{ fontSize: '0.78rem', color: '#64748b', lineHeight: 1.4 }}>{c.description}</p>
                </div>
              ))}
            </div>

            {/* Featured Courses Showcase */}
            <div className="section-header">
              <div>
                <h2>{t('sections.featured_skills')}</h2>
                <p>Popular, high-demand certifications aligned with industry requirements</p>
              </div>
            </div>

            <div className="cards-grid">
              {skills.slice(0, 6).map((s: any) => (
                <div key={s.code} className="skill-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <span className="badge-category">{s.category_name}</span>
                    <span className={`badge-level ${s.level.toLowerCase()}`}>{s.level}</span>
                  </div>
                  <h3>{s.name}</h3>
                  <p className="summary">{s.summary}</p>
                  <div className="card-meta-row">
                    <span className="meta-item"><Clock size={14} /> {s.duration_hours} Hours ({s.duration_weeks} wks)</span>
                    <span className="meta-item"><Users size={14} /> {s.enrolled_count} Enrolled</span>
                  </div>
                  <button className="btn-card-action" onClick={() => openCourseDetail(s.code)}>
                    {t('course.view_details')} <ArrowRight size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* EXPLORE COURSES CATALOGUE */}
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
                  <button
                    className="btn-primary-orange"
                    style={{ justifyContent: 'center' }}
                    onClick={() => handleStartEnrolment(p)}
                  >
                    Select Batch & Enrol
                  </button>
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

      {/* TRAINERS PROFILES */}
      {activeTab === 'trainers' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <h2>{t('sections.trainers_heading')}</h2>
              <p>Government certified Master Trainers and senior technology mentors</p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
            {trainers.map((t: any) => (
              <div key={t.code} style={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '1.5rem' }}>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', marginBottom: '1rem' }}>
                  <div style={{ width: '50px', height: '50px', borderRadius: '50%', backgroundColor: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0f2444' }}>
                    <User size={24} />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a' }}>{t.name}</h3>
                    <span style={{ fontSize: '0.78rem', color: '#ea580c', fontWeight: 600 }}>{t.specialisation}</span>
                  </div>
                </div>
                <p style={{ fontSize: '0.82rem', color: '#475569', marginBottom: '0.75rem' }}>
                  <strong>Qualification:</strong> {t.qualification}
                </p>
                <div style={{ fontSize: '0.8rem', color: '#64748b', borderTop: '1px solid #f1f5f9', paddingTop: '0.75rem' }}>
                  <div><strong>Experience:</strong> {t.experience_years} Years Industry Practice</div>
                  <div><strong>Assigned Centre:</strong> {t.centre_name}</div>
                  <div><strong>Schedule Availability:</strong> {t.availability}</div>
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
              <div style={{ flex: '2 1 320px', minWidth: '280px' }}>
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

      {/* CAREER OPPORTUNITIES (EMPLOYMENT ADAPTER) */}
      {activeTab === 'careers' && (
        <div className="main-container">
          <div className="section-header">
            <div>
              <h2>{t('careers.title')}</h2>
              <p>{t('careers.subtitle')}</p>
            </div>
          </div>

          <div style={{ display: 'grid', gap: '1.25rem' }}>
            {jobs.map((j: any) => {
              const isSaved = savedJobs.some((s: any) => s.job_id === j.id);

              return (
                <div
                  key={j.id}
                  style={{
                    backgroundColor: '#ffffff',
                    border: '1px solid #e2e8f0',
                    borderRadius: '10px',
                    padding: '1.5rem',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    flexWrap: 'wrap',
                    gap: '1.25rem'
                  }}
                >
                  <div style={{ flex: '1', minWidth: '300px' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.4rem', flexWrap: 'wrap' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#166534', backgroundColor: '#f0fdf4', padding: '0.2rem 0.6rem', borderRadius: '4px' }}>
                        {j.category}
                      </span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#1e40af', backgroundColor: '#eff6ff', padding: '0.2rem 0.6rem', borderRadius: '4px' }}>
                        {j.work_mode}
                      </span>
                      {j.is_fresher_friendly && (
                        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#ea580c', backgroundColor: '#fff7ed', padding: '0.2rem 0.6rem', borderRadius: '4px' }}>
                          {t('careers.fresher_friendly')}
                        </span>
                      )}
                    </div>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.25rem' }}>{j.title}</h3>
                    <p style={{ fontSize: '0.9rem', fontWeight: 600, color: '#334155', marginBottom: '0.4rem' }}>{j.company} • {j.location}</p>
                    <p style={{ fontSize: '0.85rem', color: '#475569', marginBottom: '0.75rem' }}>{j.description}</p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', marginBottom: '0.5rem' }}>
                      {j.required_skills?.map((sk: string) => (
                        <span key={sk} style={{ fontSize: '0.72rem', backgroundColor: '#f1f5f9', padding: '0.2rem 0.5rem', borderRadius: '4px', color: '#334155' }}>
                          {sk}
                        </span>
                      ))}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                      <strong>{t('careers.salary')}:</strong> {j.salary} • <strong>{t('careers.experience')}:</strong> {j.experience}
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', minWidth: '190px' }}>
                    <button
                      type="button"
                      className="btn-primary-orange"
                      style={{ textAlign: 'center', justifyContent: 'center' }}
                      onClick={() => handleOpenJobApplyModal(j)}
                    >
                      {t('careers.apply_portal')}
                    </button>
                    <button
                      type="button"
                      className="btn-navy-outline"
                      style={{
                        justifyContent: 'center',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        backgroundColor: isSaved ? '#eff6ff' : 'transparent',
                        borderColor: isSaved ? '#174c80' : undefined,
                        color: isSaved ? '#174c80' : undefined,
                        fontWeight: isSaved ? 700 : undefined
                      }}
                      onClick={() => handleToggleSaveJob(j)}
                    >
                      {isSaved ? <BookmarkCheck size={16} color="#174c80" /> : <Bookmark size={16} />}
                      {isSaved ? t('careers.saved') : t('careers.save_opportunity')}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
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

          {/* Sub Navigation Tabs */}
          <div className="tabs-nav" style={{ marginBottom: '1.5rem' }}>
            <button
              type="button"
              className={`tab-btn ${appsActiveSubTab === 'courses' ? 'active' : ''}`}
              onClick={() => setAppsActiveSubTab('courses')}
            >
              {t('apps.training_tab')} ({myApplications.length})
            </button>
            <button
              type="button"
              className={`tab-btn ${appsActiveSubTab === 'jobs' ? 'active' : ''}`}
              onClick={() => setAppsActiveSubTab('jobs')}
            >
              {t('apps.jobs_tab')} ({myJobApplications.length})
            </button>
            <button
              type="button"
              className={`tab-btn ${appsActiveSubTab === 'saved' ? 'active' : ''}`}
              onClick={() => setAppsActiveSubTab('saved')}
            >
              {t('careers.saved_heading')} ({savedJobs.length})
            </button>
          </div>

          {/* TAB 1: Training Enrolments */}
          {appsActiveSubTab === 'courses' && (
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

                        <div style={{ textAlign: 'right' }}>
                          <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
                            {t('apps.progress')}: {app.training_progress_pct}%
                          </div>
                          <div style={{ width: '180px', height: '8px', backgroundColor: '#e2e8f0', borderRadius: '4px', overflow: 'hidden', marginTop: '0.35rem' }}>
                            <div style={{ width: `${app.training_progress_pct}%`, height: '100%', backgroundColor: app.training_progress_pct === 100 ? '#16a34a' : '#ea580c' }} />
                          </div>
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

          {/* TAB 2: Career Applications */}
          {appsActiveSubTab === 'jobs' && (
            <>
              {myJobApplications.length === 0 ? (
                <div style={{ backgroundColor: '#ffffff', padding: '3rem', borderRadius: '10px', textAlign: 'center', border: '1px solid #e2e8f0' }}>
                  <Briefcase size={40} style={{ color: '#94a3b8', margin: '0 auto 1rem auto' }} />
                  <h3 style={{ fontSize: '1.15rem', color: '#0f172a', marginBottom: '0.5rem' }}>{t('apps.no_jobs')}</h3>
                  <button className="btn-primary-orange" style={{ margin: '0 auto' }} onClick={() => setActiveTab('careers')}>
                    {t('apps.browse_jobs')}
                  </button>
                </div>
              ) : (
                <div style={{ display: 'grid', gap: '1.25rem' }}>
                  {myJobApplications.map((app: any) => {

                    return (
                      <div key={app.application_ref} style={{ backgroundColor: '#ffffff', borderRadius: '10px', border: '1px solid #e2e8f0', padding: '1.5rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '1rem', marginBottom: '1rem' }}>
                          <div>
                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.25rem' }}>
                              <span style={{ fontSize: '0.8rem', fontWeight: 800, color: '#0f2444' }}>{app.application_ref}</span>
                              <span className="status-pill APPROVED">
                                <Check size={12} /> {app.status}
                              </span>
                            </div>
                            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a' }}>{app.job_title}</h3>
                            <p style={{ fontSize: '0.85rem', color: '#334155', fontWeight: 600 }}>{app.company} • {app.location}</p>
                            <p style={{ fontSize: '0.82rem', color: '#64748b' }}>{t('careers.applied_on')}: {formatISTDateTime(app.created_at)}</p>
                          </div>
                          <div>
                            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#166534', backgroundColor: '#f0fdf4', padding: '0.25rem 0.65rem', borderRadius: '4px' }}>
                              {app.job_id}
                            </span>
                          </div>
                        </div>

                        <div style={{ backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '6px', fontSize: '0.85rem', color: '#334155' }}>
                          <div><strong>{t('careers.full_name')}:</strong> {app.full_name} ({app.email} • {app.phone})</div>
                          {app.education && <div><strong>{t('apps.education')}:</strong> {app.education}</div>}
                          {app.experience_years && <div><strong>{t('apps.experience')}:</strong> {app.experience_years}</div>}
                          {app.statement && (
                            <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid #e2e8f0' }}>
                              <strong>{t('careers.statement')}:</strong>
                              <p style={{ margin: '0.25rem 0 0 0', color: '#475569', fontStyle: 'italic' }}>"{app.statement}"</p>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </>
          )}

          {/* TAB 3: Saved Opportunities */}
          {appsActiveSubTab === 'saved' && (
            <>
              {savedJobs.length === 0 ? (
                <div style={{ backgroundColor: '#ffffff', padding: '3rem', borderRadius: '10px', textAlign: 'center', border: '1px solid #e2e8f0' }}>
                  <Bookmark size={40} style={{ color: '#94a3b8', margin: '0 auto 1rem auto' }} />
                  <h3 style={{ fontSize: '1.15rem', color: '#0f172a', marginBottom: '0.5rem' }}>{t('careers.no_saved')}</h3>
                  <button className="btn-primary-orange" style={{ margin: '0 auto' }} onClick={() => setActiveTab('careers')}>
                    {t('apps.browse_jobs')}
                  </button>
                </div>
              ) : (
                <div style={{ display: 'grid', gap: '1.25rem' }}>
                  {savedJobs.map((sj: any) => {
                    const fullJob = jobs.find((j: any) => j.id === sj.job_id);

                    return (
                      <div
                        key={sj.id}
                        style={{
                          backgroundColor: '#ffffff',
                          border: '1px solid #e2e8f0',
                          borderRadius: '10px',
                          padding: '1.5rem',
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          flexWrap: 'wrap',
                          gap: '1.25rem'
                        }}
                      >
                        <div style={{ flex: '1', minWidth: '300px' }}>
                          <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#174c80', backgroundColor: '#eff6ff', padding: '0.2rem 0.5rem', borderRadius: '4px' }}>
                            {sj.job_id}
                          </span>
                          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#0f172a', margin: '0.35rem 0 0.2rem 0' }}>{sj.title}</h3>
                          <p style={{ fontSize: '0.9rem', fontWeight: 600, color: '#334155', marginBottom: '0.35rem' }}>{sj.company} • {sj.location}</p>
                          <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                            <strong>{t('careers.salary')}:</strong> {sj.salary || 'Competitive'} • <strong>{t('careers.experience')}:</strong> {sj.experience || 'As per norms'}
                          </div>
                          <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: '0.4rem' }}>
                            {t('careers.date_saved')}: {new Date(sj.saved_at).toLocaleDateString()}
                          </div>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', minWidth: '180px' }}>
                          <button
                            type="button"
                            className="btn-primary-orange"
                            style={{ textAlign: 'center', justifyContent: 'center' }}
                            onClick={() => {
                              if (fullJob) handleOpenJobApplyModal(fullJob);
                              else handleOpenJobApplyModal({ id: sj.job_id, title: sj.title, company: sj.company, location: sj.location });
                            }}
                          >
                            {t('careers.apply_portal')}
                          </button>
                          <button
                            type="button"
                            className="btn-navy-outline"
                            style={{ justifyContent: 'center', color: '#dc2626', borderColor: '#fca5a5' }}
                            onClick={() => handleToggleSaveJob({ id: sj.job_id, title: sj.title })}
                          >
                            {t('careers.unsave')}
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </>
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

      {/* COMPREHENSIVE 8-SECTION ENROLMENT MODAL */}
      {enrollingProgram && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '820px', maxHeight: '92vh', overflowY: 'auto' }}>
            <div className="modal-header">
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f2444' }}>
                  Government Training Programme Enrolment Dossier
                </h3>
                <span style={{ fontSize: '0.78rem', color: '#64748b' }}>
                  Standard NSQF Skill Development Application (Sections A – H)
                </span>
              </div>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setEnrollingProgram(null)}>
                <X size={20} />
              </button>
            </div>

            <div className="modal-body" style={{ display: 'grid', gap: '1.25rem' }}>
              <div style={{ backgroundColor: '#f1f5f9', borderLeft: '4px solid #ea580c', padding: '1rem', borderRadius: '4px' }}>
                <div style={{ fontWeight: 700, color: '#0f172a', fontSize: '1.05rem' }}>{enrollingProgram.title}</div>
                <div style={{ fontSize: '0.82rem', color: '#475569', marginTop: '0.2rem' }}>
                  Category: {enrollingProgram.skill?.category || 'National Skill Qualification'} | Fee: {enrollingProgram.fee === 0 ? 'Free / Fully Subsidized' : `₹${enrollingProgram.fee}`}
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

              {/* Verified Citizen Autofill Banner */}
              <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.6rem 0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', color: '#166534' }}>
                <CheckCircle2 size={16} style={{ color: '#16a34a', flexShrink: 0 }} />
                <span><strong>Smart Form Autofill:</strong> Applicant information has been automatically populated from your verified Citizen Profile. You can review and update any details before submission.</span>
              </div>

              {/* SECTION A: Personal Details */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.4rem' }}>
                  Section A: Applicant Personal Information
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label>Name:</label>
                    <input type="text" className="form-control" value={appFullName} onChange={(e) => setAppFullName(e.target.value)} placeholder="Name as per Aadhaar Card" />
                  </div>
                  <div className="form-group">
                    <label>Citizen Ref / ID:</label>
                    <input type="text" className="form-control" value={citizenRef || 'CIT-2026-X'} disabled style={{ backgroundColor: '#f8fafc' }} />
                  </div>
                  <div className="form-group">
                    <label>Email Address:</label>
                    <input type="email" className="form-control" value={appEmail} onChange={(e) => setAppEmail(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Mobile Number:</label>
                    <input type="tel" className="form-control" value={appPhone} onChange={(e) => setAppPhone(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Date of Birth:</label>
                    <input type="date" className="form-control" value={appDob} onChange={(e) => setAppDob(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Gender:</label>
                    <select className="form-control" value={appGender} onChange={(e) => setAppGender(e.target.value)}>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Transgender">Transgender</option>
                      <option value="Prefer not to say">Prefer not to say</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* SECTION B: Address Details */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.4rem' }}>
                  Section B: Residential & Contact Address
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label>Street Address / Premise:</label>
                    <input type="text" className="form-control" value={appAddress} onChange={(e) => setAppAddress(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>City / District:</label>
                    <input type="text" className="form-control" value={appCity} onChange={(e) => setAppCity(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>State:</label>
                    <input type="text" className="form-control" value={appState} onChange={(e) => setAppState(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>PIN Code:</label>
                    <input type="text" className="form-control" value={appPincode} onChange={(e) => setAppPincode(e.target.value)} />
                  </div>
                </div>
              </div>

              {/* SECTION C: Education Background */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.4rem' }}>
                  Section C: Educational Qualifications
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label>Highest Qualification:</label>
                    <select className="form-control" value={appEducation} onChange={(e) => setAppEducation(e.target.value)}>
                      <option value="Secondary School (10th)">Secondary School (10th)</option>
                      <option value="Higher Secondary (12th / PUC)">Higher Secondary (12th / PUC)</option>
                      <option value="Diploma / Polytechnic">Diploma / Polytechnic</option>
                      <option value="Bachelor of Engineering / Science">Bachelor of Engineering / Science</option>
                      <option value="Bachelor of Commerce / Arts">Bachelor of Commerce / Arts</option>
                      <option value="Master of Technology / Science">Master of Technology / Science</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Institution / University:</label>
                    <input type="text" className="form-control" value={appInstitution} onChange={(e) => setAppInstitution(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Specialization / Branch:</label>
                    <input type="text" className="form-control" value={appSpecialization} onChange={(e) => setAppSpecialization(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Year of Passing:</label>
                    <input type="text" className="form-control" value={appGradYear} onChange={(e) => setAppGradYear(e.target.value)} />
                  </div>
                </div>
              </div>

              {/* SECTION D: Employment Background */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.4rem' }}>
                  Section D: Employment & Professional Background
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label>Employment Status:</label>
                    <select className="form-control" value={appEmploymentStatus} onChange={(e) => setAppEmploymentStatus(e.target.value)}>
                      <option value="Job Seeker">Job Seeker</option>
                      <option value="Student / Scholar">Student / Scholar</option>
                      <option value="Employed">Employed</option>
                      <option value="Self-Employed / Freelancer">Self-Employed / Freelancer</option>
                      <option value="Apprentice">Apprentice</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Current Occupation / Field:</label>
                    <input type="text" className="form-control" value={appOccupation} onChange={(e) => setAppOccupation(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Total Experience (Years):</label>
                    <input type="number" min={0} max={40} className="form-control" value={appExperienceYears} onChange={(e) => setAppExperienceYears(Number(e.target.value))} />
                  </div>
                </div>
              </div>

              {/* SECTION E: Training Preferences */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.4rem' }}>
                  Section E: Training Batch & Preference Selection
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem' }}>
                  <div className="form-group" style={{ gridColumn: 'span 2' }}>
                    <label>Select Training Batch (Real-time seat capacity checked):</label>
                    <select
                      className="form-control"
                      value={selectedBatchId || ''}
                      onChange={(e) => setSelectedBatchId(Number(e.target.value))}
                    >
                      {enrollingProgram.batches?.map((b: any) => (
                        <option key={b.id} value={b.id}>
                          {b.batch_name} ({b.timings} - {b.mode}) - {b.available_seats} / {b.total_seats} seats remaining
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Preferred Delivery Mode:</label>
                    <select className="form-control" value={appPrefMode} onChange={(e) => setAppPrefMode(e.target.value)}>
                      <option value="Hybrid">Hybrid (Online Lectures + Physical Labs)</option>
                      <option value="Online">Online Interactive</option>
                      <option value="Classroom">Classroom Full-Time</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Preferred Slot:</label>
                    <select className="form-control" value={appPrefTiming} onChange={(e) => setAppPrefTiming(e.target.value)}>
                      <option value="Morning (09:00 AM - 12:00 PM)">Morning (09:00 AM - 12:00 PM)</option>
                      <option value="Afternoon (02:00 PM - 05:00 PM)">Afternoon (02:00 PM - 05:00 PM)</option>
                      <option value="Weekend Intensive">Weekend Intensive (Sat-Sun)</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* SECTION F: Motivation & Career Goals */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.4rem' }}>
                  Section F: Statement of Purpose & Career Goals
                </h4>
                <div className="form-group" style={{ marginBottom: '0.75rem' }}>
                  <label>Applicant Motivation / Statement of Purpose (Mandatory):</label>
                  <textarea
                    className="form-control"
                    rows={3}
                    value={enrolmentStatement}
                    onChange={(e) => setEnrolmentStatement(e.target.value)}
                    placeholder="Describe why you wish to enrol in this programme, your learning objectives, and intended career trajectory..."
                  />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label>Target Competencies to Master:</label>
                    <input type="text" className="form-control" value={appTargetSkills} onChange={(e) => setAppTargetSkills(e.target.value)} />
                  </div>
                  <div className="form-group" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', paddingTop: '1.5rem' }}>
                    <input
                      type="checkbox"
                      id="placementAssistCheck"
                      checked={appPostJobPlacement}
                      onChange={(e) => setAppPostJobPlacement(e.target.checked)}
                    />
                    <label htmlFor="placementAssistCheck" style={{ margin: 0, fontSize: '0.82rem', fontWeight: 600 }}>
                      Opt-in for Career Placement & Apprenticeship Linkage
                    </label>
                  </div>
                </div>
              </div>

              {/* SECTION G: Supporting Documents / Credentials */}
              <div style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#ffffff' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.75rem', borderBottom: '1px solid #f1f5f9', paddingBottom: '0.4rem' }}>
                  Section G: Identity & Eligibility Verification
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                  <div className="form-group">
                    <label>Identity Proof Document Type:</label>
                    <select className="form-control" value={appIdProofType} onChange={(e) => setAppIdProofType(e.target.value)}>
                      <option value="Aadhaar / National Identity Card">Aadhaar / National Identity Card</option>
                      <option value="Voter Identification Card">Voter Identification Card</option>
                      <option value="Passport">Passport</option>
                      <option value="State Driving Licence">State Driving Licence</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Document Reference / Masked Number:</label>
                    <input type="text" className="form-control" value={appIdProofNumber} onChange={(e) => setAppIdProofNumber(e.target.value)} />
                  </div>
                </div>
                <div className="form-group" style={{ marginTop: '0.5rem' }}>
                  <label>Document Attachment / Locker Note:</label>
                  <input type="text" className="form-control" value={appDocAttachedNote} onChange={(e) => setAppDocAttachedNote(e.target.value)} />
                </div>
              </div>

              {/* SECTION H: Declaration & Consent */}
              <div style={{ border: '1px solid #fed7aa', backgroundColor: '#fff7ed', borderRadius: '8px', padding: '1.25rem' }}>
                <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#9a3412', marginBottom: '0.5rem' }}>
                  Section H: Statutory Citizen Declaration & Consent
                </h4>
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
                  <input
                    type="checkbox"
                    id="enrolDeclaration"
                    checked={appDeclarationAgreed}
                    onChange={(e) => setAppDeclarationAgreed(e.target.checked)}
                    style={{ marginTop: '0.25rem' }}
                  />
                  <label htmlFor="enrolDeclaration" style={{ fontSize: '0.82rem', color: '#7c2d12', lineHeight: 1.45 }}>
                    I hereby declare that all particulars furnished in this application (Sections A through H) are true and correct to the best of my knowledge and belief. I agree to abide by the minimum attendance benchmark (75%) and continuous evaluation guidelines required for official NSQF competency certification under the NagrikSetu Skill Development Service.
                  </label>
                </div>
              </div>

              {/* MANDATORY MOBILE OTP VERIFICATION */}
              <div style={{ border: '1px solid #cbd5e1', borderRadius: '8px', padding: '1.25rem', backgroundColor: '#f8fafc' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f2444', margin: 0 }}>
                    Mandatory Mobile Verification (SMS OTP)
                  </h4>
                  {enrolOtpVerified && (
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#16a34a', backgroundColor: '#dcfce7', padding: '0.2rem 0.5rem', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <CheckCircle2 size={13} /> Verified
                    </span>
                  )}
                </div>
                <p style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '0.75rem' }}>
                  A one-time verification code is required to confirm submission of this official skill training application to registered phone: <strong>{appPhone || myProfile?.phone || 'Your Phone'}</strong>.
                </p>

                {!enrolOtpVerified ? (
                  <div style={{ display: 'grid', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      {!enrolOtpSent ? (
                        <button
                          type="button"
                          className="btn-navy-outline"
                          onClick={handleSendEnrolOtp}
                          disabled={enrolOtpLoading}
                        >
                          {enrolOtpLoading ? 'Sending SMS OTP...' : 'Send SMS OTP to Registered Mobile'}
                        </button>
                      ) : (
                        <>
                          <input
                            type="text"
                            maxLength={6}
                            className="form-control"
                            style={{ maxWidth: '180px', letterSpacing: '4px', fontWeight: 700, textAlign: 'center', fontSize: '1.1rem' }}
                            value={enrolOtpCode}
                            onChange={(e) => setEnrolOtpCode(e.target.value.replace(/\D/g, ''))}
                            placeholder="••••••"
                          />
                          <button
                            type="button"
                            className="btn-primary-orange"
                            onClick={handleVerifyEnrolOtp}
                            disabled={enrolOtpLoading || enrolOtpCode.length !== 6}
                          >
                            {enrolOtpLoading ? 'Verifying...' : 'Verify Code'}
                          </button>
                          <button
                            type="button"
                            className="btn-navy-outline"
                            onClick={handleSendEnrolOtp}
                            disabled={enrolOtpLoading || enrolOtpCooldown > 0}
                          >
                            {enrolOtpCooldown > 0 ? `Resend (${enrolOtpCooldown}s)` : 'Resend'}
                          </button>
                        </>
                      )}
                    </div>
                    {enrolOtpMsg && (
                      <div style={{ fontSize: '0.78rem', color: enrolOtpMsg.type === 'success' ? '#15803d' : '#b91c1c' }}>
                        {enrolOtpMsg.text}
                      </div>
                    )}
                  </div>
                ) : (
                  <div style={{ fontSize: '0.82rem', color: '#166534', fontWeight: 600 }}>
                    Verification reference: <code>{enrolOtpRef}</code> confirmed. Application ready to submit.
                  </div>
                )}
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '0.5rem' }}>
                <button className="btn-navy-outline" onClick={() => setEnrollingProgram(null)} disabled={enrolSubmitting}>
                  Cancel
                </button>
                <button className="btn-primary-orange" onClick={handleEnrolmentSubmit} disabled={enrolSubmitting}>
                  {enrolSubmitting ? 'Submitting Application...' : 'Confirm & Submit Application'}
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
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444' }}>Review Application {reviewModalApp.application_id}</h3>
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

              <div className="form-group">
                <label>Administrative Decision Status:</label>
                <select className="form-control" value={reviewStatus} onChange={(e) => setReviewStatus(e.target.value)}>
                  <option value="UNDER_REVIEW">UNDER_REVIEW</option>
                  <option value="APPROVED">APPROVED</option>
                  <option value="REJECTED">REJECTED</option>
                  <option value="ADDITIONAL_INFORMATION_REQUIRED">ADDITIONAL_INFORMATION_REQUIRED</option>
                  <option value="COMPLETED">COMPLETED</option>
                </select>
              </div>

              <div className="form-group">
                <label>Official Remarks / Reason (Mandatory):</label>
                <textarea
                  className="form-control"
                  rows={3}
                  value={reviewRemarks}
                  onChange={(e) => setReviewRemarks(e.target.value)}
                  placeholder="Enter official review remarks for the citizen..."
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button className="btn-navy-outline" onClick={() => setReviewModalApp(null)}>
                  Cancel
                </button>
                <button className="btn-primary-orange" onClick={handleAdminReviewSubmit}>
                  Save Decision
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* LOGIN MODAL */}
      {showLoginModal && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '420px' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444' }}>
                {isAdminLogin ? 'Admin Login' : 'Login'}
              </h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setShowLoginModal(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              {authError && (
                <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.6rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem' }}>
                  {authError}
                </div>
              )}
              <form onSubmit={handleLogin}>
                {/* Method selector for citizen login */}
                {!isAdminLogin && (
                  <div style={{ display: 'flex', gap: '0.4rem', marginBottom: '1.2rem', background: '#f1f5f9', padding: '0.25rem', borderRadius: '8px' }}>
                    <button
                      type="button"
                      onClick={() => { setLoginMethod('password'); setAuthError(''); }}
                      style={{
                        flex: 1,
                        padding: '0.45rem',
                        borderRadius: '6px',
                        border: 'none',
                        fontWeight: 700,
                        fontSize: '0.8rem',
                        cursor: 'pointer',
                        background: loginMethod === 'password' ? '#ffffff' : 'transparent',
                        color: loginMethod === 'password' ? '#0f2444' : '#64748b',
                        boxShadow: loginMethod === 'password' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
                      }}
                    >
                      🔑 Password Login
                    </button>
                    <button
                      type="button"
                      onClick={() => { setLoginMethod('otp'); setAuthError(''); }}
                      style={{
                        flex: 1,
                        padding: '0.45rem',
                        borderRadius: '6px',
                        border: 'none',
                        fontWeight: 700,
                        fontSize: '0.8rem',
                        cursor: 'pointer',
                        background: loginMethod === 'otp' ? '#ffffff' : 'transparent',
                        color: loginMethod === 'otp' ? '#0f2444' : '#64748b',
                        boxShadow: loginMethod === 'otp' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
                      }}
                    >
                      📱 Instant Email OTP
                    </button>
                  </div>
                )}

                <div className="form-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                    <label style={{ margin: 0 }}>
                      {isAdminLogin ? 'Administrator Email:' : 'Registered Email Address:'}
                    </label>
                    {!isAdminLogin && loginMethod === 'otp' && loginOtpDemoMode && (
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#b45309', backgroundColor: '#fef3c7', padding: '0.15rem 0.45rem', borderRadius: '4px', border: '1px solid #fde68a' }}>
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
                      placeholder={isAdminLogin ? "skill.admin@nagriksetu.local" : "e.g. karthik@example.com"}
                      disabled={loginMethod === 'otp' && loginOtpVerified}
                    />
                    {!isAdminLogin && loginMethod === 'otp' && (
                      <button
                        type="button"
                        className="btn-navy-outline"
                        style={{ whiteSpace: 'nowrap', padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}
                        onClick={handleSendLoginOtp}
                        disabled={loginOtpLoading || loginOtpCooldown > 0 || loginOtpVerified}
                      >
                        {loginOtpVerified ? 'Verified' : (loginOtpCooldown > 0 ? `Resend (${loginOtpCooldown}s)` : (loginOtpSent ? 'Resend OTP' : 'Send OTP'))}
                      </button>
                    )}
                  </div>
                  {!isAdminLogin && loginMethod === 'otp' && loginOtpVerified && (
                    <div style={{ color: '#16a34a', fontSize: '0.78rem', marginTop: '0.3rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                      <CheckCircle2 size={14} /> Email verified successfully.
                    </div>
                  )}
                </div>

                {/* Email OTP Verification Section for Passwordless Citizen Login */}
                {!isAdminLogin && loginMethod === 'otp' && loginOtpSent && !loginOtpVerified && (
                  <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.75rem', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#166534', margin: 0 }}>
                        Enter 6-Digit Email OTP:
                      </label>
                      <span style={{ fontSize: '0.75rem', color: loginOtpExpirySec > 0 ? '#15803d' : '#b91c1c', fontWeight: 600 }}>
                        {loginOtpExpirySec > 0 ? `Expires in ${Math.floor(loginOtpExpirySec / 60)}:${(loginOtpExpirySec % 60).toString().padStart(2, '0')}` : 'OTP Expired'}
                      </span>
                    </div>

                    {loginOtpDemoMode && loginOtpDemoCode && (
                      <div style={{ backgroundColor: '#fef3c7', border: '1px solid #fde68a', borderRadius: '4px', padding: '0.4rem 0.6rem', marginBottom: '0.5rem', fontSize: '0.78rem', color: '#92400e' }}>
                        <strong>[Demo Mode Inspection]:</strong> Generated OTP is <code>{loginOtpDemoCode}</code> (No real email sent).
                      </div>
                    )}

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

                {/* Password field shown in Password mode and Admin mode */}
                {(isAdminLogin || loginMethod === 'password') && (
                  <div className="form-group">
                    <label>{isAdminLogin ? 'Administrator Password:' : 'Account Password:'}</label>
                    <input
                      type="password"
                      required
                      className="form-control"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      placeholder={isAdminLogin ? "Enter administrator password" : "Enter your account password"}
                    />
                  </div>
                )}

                <button
                  type="submit"
                  className="btn-primary-orange"
                  style={{ width: '100%', justifyContent: 'center' }}
                  disabled={
                    authLoading ||
                    !loginEmail.trim() ||
                    (isAdminLogin ? !loginPassword.trim() : (loginMethod === 'password' ? !loginPassword.trim() : !loginOtpVerified))
                  }
                >
                  {authLoading ? 'Logging In...' : (isAdminLogin ? 'Login as Administrator' : 'Login')}
                </button>
              </form>

              <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem' }}>
                <button
                  type="button"
                  style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', textDecoration: 'underline' }}
                  onClick={() => {
                    const nextAdmin = !isAdminLogin;
                    setIsAdminLogin(nextAdmin);
                    setAuthError('');
                    if (nextAdmin) {
                      setLoginMethod('password');
                      if (!loginEmail) setLoginEmail('skill.admin@nagriksetu.local');
                      if (!loginPassword) setLoginPassword('SkillAdmin@2026!');
                    }
                  }}
                >
                  {isAdminLogin ? '← Switch to Citizen Login' : 'Admin Login (with Password)'}
                </button>
                <button
                  style={{ background: 'none', border: 'none', color: '#ea580c', fontWeight: 700, cursor: 'pointer' }}
                  onClick={() => { setShowLoginModal(false); setShowRegisterModal(true); }}
                >
                  Register Now
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* REGISTER MODAL */}
      {showRegisterModal && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '440px' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444' }}>Create Account</h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setShowRegisterModal(false)}>
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              {authError && (
                <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.6rem', borderRadius: '6px', fontSize: '0.8rem', marginBottom: '1rem' }}>
                  {authError}
                </div>
              )}
              <form onSubmit={handleRegister}>
                <div className="form-group">
                  <label>Name:</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    value={regFullName}
                    onChange={(e) => setRegFullName(e.target.value)}
                    placeholder="Name as per Aadhaar Card"
                  />
                </div>
                <div className="form-group">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.3rem' }}>
                    <label style={{ margin: 0 }}>Email Address:</label>
                    {regOtpDemoMode && (
                      <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#b45309', backgroundColor: '#fef3c7', padding: '0.15rem 0.45rem', borderRadius: '4px', border: '1px solid #fde68a' }}>
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
                        // Invalidate verification if email changes
                        if (regOtpVerified || regOtpSent) {
                          setRegOtpVerified(false);
                          setRegOtpSent(false);
                          setRegOtpRef('');
                          setRegOtpCode('');
                          setRegOtpMsg(null);
                          setRegOtpDemoCode('');
                        }
                      }}
                      placeholder="e.g. karthik@example.com"
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

                {/* Email OTP Verification Section directly below email */}
                {regOtpSent && !regOtpVerified && (
                  <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.75rem', marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                      <label style={{ fontSize: '0.82rem', fontWeight: 600, color: '#166534', margin: 0 }}>
                        Enter 6-Digit Email OTP:
                      </label>
                      <span style={{ fontSize: '0.75rem', color: regOtpExpirySec > 0 ? '#15803d' : '#b91c1c', fontWeight: 600 }}>
                        {regOtpExpirySec > 0 ? `Expires in ${Math.floor(regOtpExpirySec / 60)}:${(regOtpExpirySec % 60).toString().padStart(2, '0')}` : 'OTP Expired'}
                      </span>
                    </div>

                    {/* Development Demo Mode Inspection Box */}
                    {regOtpDemoMode && regOtpDemoCode && (
                      <div style={{ backgroundColor: '#fef3c7', border: '1px solid #fde68a', borderRadius: '4px', padding: '0.4rem 0.6rem', marginBottom: '0.5rem', fontSize: '0.78rem', color: '#92400e' }}>
                        <strong>[Demo Mode Inspection]:</strong> Generated OTP is <code>{regOtpDemoCode}</code> (No real email sent).
                      </div>
                    )}

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
                        {regOtpLoading ? 'Verifying...' : 'Verify OTP'}
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
                  <label>Mobile Number:</label>
                  <input
                    type="tel"
                    required
                    className="form-control"
                    value={regPhone}
                    onChange={(e) => setRegPhone(e.target.value)}
                    placeholder="+91 9876543210"
                  />
                </div>
                <div className="form-group">
                  <label>Create Account Password:</label>
                  <input
                    type="password"
                    required
                    className="form-control"
                    value={regPassword}
                    onChange={(e) => setRegPassword(e.target.value)}
                    placeholder="Choose a secure password (min 6 characters)"
                  />
                </div>
                <button type="submit" className="btn-primary-orange" style={{ width: '100%', justifyContent: 'center' }} disabled={authLoading || !regOtpVerified || !regPassword.trim()}>
                  {authLoading ? 'Registering...' : 'Create Citizen Account'}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* MODAL: ADD SKILL COURSE */}
      {showAddSkillModal && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '540px' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444' }}>Create New Skill Course</h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setShowAddSkillModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleAdminCreateSkill} className="modal-body">
              <div className="form-group">
                <label>Skill Name:</label>
                <input
                  type="text"
                  required
                  className="form-control"
                  placeholder="e.g. Next.js Full Stack Architecture"
                  value={newSkillName}
                  onChange={(e) => setNewSkillName(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Category:</label>
                <select className="form-control" value={newSkillCategory} onChange={(e) => setNewSkillCategory(e.target.value)}>
                  {categories.map((c: any) => (
                    <option key={c.code} value={c.name}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
                <div className="form-group">
                  <label>Proficiency Level:</label>
                  <select className="form-control" value={newSkillLevel} onChange={(e) => setNewSkillLevel(e.target.value)}>
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Hours:</label>
                  <input type="number" className="form-control" value={newSkillHours} onChange={(e) => setNewSkillHours(Number(e.target.value))} />
                </div>
                <div className="form-group">
                  <label>Weeks:</label>
                  <input type="number" className="form-control" value={newSkillWeeks} onChange={(e) => setNewSkillWeeks(Number(e.target.value))} />
                </div>
              </div>
              <div className="form-group">
                <label>Course Summary & Outcomes:</label>
                <textarea
                  className="form-control"
                  rows={3}
                  required
                  placeholder="Brief summary of skills acquired and industry relevance..."
                  value={newSkillSummary}
                  onChange={(e) => setNewSkillSummary(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button type="button" className="btn-navy-outline" onClick={() => setShowAddSkillModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary-orange">Save to MySQL Catalogue</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: ADD TRAINING PROGRAMME */}
      {showAddProgrammeModal && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '600px' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444' }}>Create Training Programme & Batch</h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setShowAddProgrammeModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleAdminCreateProgramme} className="modal-body">
              <div className="form-group">
                <label>Programme Title:</label>
                <input
                  type="text"
                  required
                  className="form-control"
                  placeholder="e.g. Advanced Web Microservices Bootcamp"
                  value={newProgTitle}
                  onChange={(e) => setNewProgTitle(e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Associated Skill:</label>
                <select className="form-control" value={newProgSkillId} onChange={(e) => setNewProgSkillId(Number(e.target.value))}>
                  {skills.map((s: any) => (
                    <option key={s.id} value={s.id}>{s.name} ({s.code})</option>
                  ))}
                </select>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.5rem' }}>
                <div className="form-group">
                  <label>Mode:</label>
                  <select className="form-control" value={newProgMode} onChange={(e) => setNewProgMode(e.target.value)}>
                    <option value="Online">Online</option>
                    <option value="Classroom">Classroom</option>
                    <option value="Hybrid">Hybrid</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Duration (Hours):</label>
                  <input type="number" className="form-control" value={newProgHours} onChange={(e) => setNewProgHours(Number(e.target.value))} />
                </div>
                <div className="form-group">
                  <label>Fee (0 = Free):</label>
                  <input type="number" className="form-control" value={newProgFee} onChange={(e) => setNewProgFee(Number(e.target.value))} />
                </div>
              </div>
              <div className="form-group">
                <label>Programme Description:</label>
                <textarea
                  className="form-control"
                  rows={2}
                  required
                  value={newProgDesc}
                  onChange={(e) => setNewProgDesc(e.target.value)}
                />
              </div>

              <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '0.75rem', marginTop: '0.5rem' }}>
                <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0f2444', marginBottom: '0.5rem' }}>Initial Batch Allocation (Concurrency & Capacity):</h4>
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '0.5rem' }}>
                  <div className="form-group">
                    <label>Batch Name:</label>
                    <input type="text" className="form-control" value={newProgBatchName} onChange={(e) => setNewProgBatchName(e.target.value)} />
                  </div>
                  <div className="form-group">
                    <label>Total Capacity (Seats):</label>
                    <input type="number" className="form-control" value={newProgBatchSeats} onChange={(e) => setNewProgBatchSeats(Number(e.target.value))} />
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" className="btn-navy-outline" onClick={() => setShowAddProgrammeModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary-orange">Publish Programme to MySQL</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: ADD TRAINING CENTRE */}
      {showAddCentreModal && (
        <div className="modal-overlay">
          <div className="modal-content-lg" style={{ maxWidth: '540px' }}>
            <div className="modal-header">
              <h3 style={{ fontSize: '1.2rem', fontWeight: 800, color: '#0f2444' }}>Add Accredited Training Centre</h3>
              <button style={{ background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => setShowAddCentreModal(false)}>
                <X size={20} />
              </button>
            </div>
            <form onSubmit={handleAdminCreateCentre} className="modal-body">
              <div className="form-group">
                <label>Centre Name:</label>
                <input
                  type="text"
                  required
                  className="form-control"
                  placeholder="e.g. Belagavi District Advanced Skilling Hub"
                  value={newCentreName}
                  onChange={(e) => setNewCentreName(e.target.value)}
                />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                <div className="form-group">
                  <label>City / Location:</label>
                  <input type="text" required className="form-control" placeholder="e.g. Belagavi" value={newCentreLocation} onChange={(e) => setNewCentreLocation(e.target.value)} />
                </div>
                <div className="form-group">
                  <label>District:</label>
                  <input type="text" required className="form-control" value={newCentreDistrict} onChange={(e) => setNewCentreDistrict(e.target.value)} />
                </div>
              </div>
              <div className="form-group">
                <label>Full Address:</label>
                <textarea rows={2} required className="form-control" value={newCentreAddress} onChange={(e) => setNewCentreAddress(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Key Facilities:</label>
                <input type="text" className="form-control" value={newCentreFacilities} onChange={(e) => setNewCentreFacilities(e.target.value)} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button type="button" className="btn-navy-outline" onClick={() => setShowAddCentreModal(false)}>Cancel</button>
                <button type="submit" className="btn-primary-orange">Save Centre in MySQL</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* APPLY ON PORTAL MODAL */}
      {applyingJob && (
        <div className="modal-overlay" onClick={() => setApplyingJob(null)}>
          <div
            className="modal-content-lg"
            onClick={(e) => e.stopPropagation()}
            style={{
              maxWidth: '720px',
              height: '92vh',
              maxHeight: '92vh',
              display: 'flex',
              flexDirection: 'column',
              borderRadius: '12px',
              boxShadow: '0 24px 50px rgba(11, 39, 66, 0.35)',
              overflow: 'hidden'
            }}
          >
            {/* Fixed Modal Header */}
            <div className="modal-header" style={{ flexShrink: 0, padding: '1.15rem 1.75rem' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 800, color: '#ea580c', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {applyingJob.id} • Official Portal Application
                </span>
                <h3 style={{ margin: '0.2rem 0 0 0', fontSize: '1.25rem', fontWeight: 800, color: '#0f2444' }}>
                  Apply for Opportunity
                </h3>
              </div>
              <button
                type="button"
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b', padding: '4px', borderRadius: '4px' }}
                onClick={() => setApplyingJob(null)}
                aria-label="Close application dialog"
              >
                <X size={22} />
              </button>
            </div>

            {/* Form Container with Flex Structure */}
            <form onSubmit={handleSubmitJobApplication} className="modal-form-layout" style={{ flex: '1 1 auto', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
              {/* Independently Scrollable Body Area */}
              <div className="modal-body-scrollable">
                {/* Opportunity Details Summary Card */}
                <div style={{ backgroundColor: '#f8fafc', padding: '1.15rem', borderRadius: '8px', border: '1px solid #e2e8f0', marginBottom: '1.25rem' }}>
                  <h4 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#0f2444', margin: '0 0 0.35rem 0' }}>
                    {applyingJob.title}
                  </h4>
                  <p style={{ fontSize: '0.88rem', color: '#334155', fontWeight: 600, margin: '0 0 0.4rem 0' }}>
                    {applyingJob.company} • {applyingJob.location}
                  </p>
                  <p style={{ fontSize: '0.82rem', color: '#475569', margin: '0 0 0.65rem 0', lineHeight: 1.5 }}>
                    {applyingJob.description}
                  </p>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '0.6rem', fontSize: '0.8rem', color: '#64748b', paddingTop: '0.65rem', borderTop: '1px solid #e2e8f0' }}>
                    <div><strong>Salary / Stipend:</strong> {applyingJob.salary || 'Competitive / Government Subsidized'}</div>
                    <div><strong>Experience:</strong> {applyingJob.experience || 'Freshers Eligible'}</div>
                    <div><strong>Qualification:</strong> {applyingJob.qualification || 'Relevant Degree / Certification'}</div>
                  </div>
                  {applyingJob.required_skills && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.65rem' }}>
                      {applyingJob.required_skills.map((sk: string) => (
                        <span key={sk} style={{ fontSize: '0.72rem', backgroundColor: '#e2e8f0', padding: '0.18rem 0.5rem', borderRadius: '4px', color: '#334155', fontWeight: 600 }}>
                          {sk}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {jobApplyMsg && (
                  <div style={{
                    padding: '0.85rem 1rem',
                    borderRadius: '6px',
                    marginBottom: '1.25rem',
                    fontSize: '0.85rem',
                    backgroundColor: jobApplyMsg.type === 'success' ? '#f0fdf4' : '#fef2f2',
                    color: jobApplyMsg.type === 'success' ? '#166534' : '#991b1b',
                    border: `1px solid ${jobApplyMsg.type === 'success' ? '#bbf7d0' : '#fecaca'}`
                  }}>
                    {jobApplyMsg.text}
                  </div>
                )}

                {/* Smart Form Autofill Notice */}
                <div style={{ backgroundColor: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '6px', padding: '0.55rem 0.85rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: '#166534' }}>
                  <CheckCircle2 size={15} style={{ color: '#16a34a', flexShrink: 0 }} />
                  <span><strong>Pre-filled from Profile:</strong> Your applicant details have been loaded from your citizen record. Verify or edit before applying.</span>
                </div>

                {/* Candidate Form Fields */}
                <div className="form-group">
                  <label>Name *</label>
                  <input
                    type="text"
                    required
                    className="form-control"
                    placeholder="Name as per Aadhaar Card"
                    value={jobApplyFullName}
                    onChange={(e) => setJobApplyFullName(e.target.value)}
                  />
                </div>

                <div className="modal-form-row">
                  <div className="form-group">
                    <label>Email Address *</label>
                    <input
                      type="email"
                      required
                      className="form-control"
                      placeholder="citizen@example.com"
                      value={jobApplyEmail}
                      onChange={(e) => setJobApplyEmail(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Mobile Number *</label>
                    <input
                      type="tel"
                      required
                      className="form-control"
                      placeholder="+91 9876543210"
                      value={jobApplyPhone}
                      onChange={(e) => setJobApplyPhone(e.target.value)}
                    />
                  </div>
                </div>

                <div className="modal-form-row">
                  <div className="form-group">
                    <label>Education Qualification</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="Highest educational degree"
                      value={jobApplyEducation}
                      onChange={(e) => setJobApplyEducation(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label>Work Experience</label>
                    <input
                      type="text"
                      className="form-control"
                      placeholder="e.g. 0-1 Years / Fresher"
                      value={jobApplyExperience}
                      onChange={(e) => setJobApplyExperience(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-group" style={{ marginBottom: '0.5rem' }}>
                  <label>Statement of Purpose / Why are you interested?</label>
                  <textarea
                    rows={3}
                    className="form-control"
                    placeholder="Briefly state your qualifications and motivation for this role..."
                    value={jobApplyStatement}
                    onChange={(e) => setJobApplyStatement(e.target.value)}
                  />
                </div>
              </div>

              {/* Fixed Modal Footer: Cancel and Submit Application */}
              <div className="modal-footer-fixed">
                <button
                  type="button"
                  className="btn-navy-outline"
                  onClick={() => setApplyingJob(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-primary-orange"
                  disabled={jobApplyLoading}
                >
                  {jobApplyLoading ? 'Submitting Application...' : 'Submit Application'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

                  {/* FOOTER */}
      {/* 4px Indian Flag Tricolor Ribbon */}
      <div style={{ height: '4px', width: '100%', background: 'linear-gradient(to right, #FF9933 0%, #FF9933 33.3%, #FFFFFF 33.3%, #FFFFFF 66.6%, #138808 66.6%, #138808 100%)', marginTop: '4rem' }} />
      <footer style={{ backgroundColor: '#081c33', color: '#94a3b8', padding: '3rem 1.5rem 1.5rem 1.5rem' }}>
        <div style={{ maxWidth: '1360px', margin: '0 auto' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '2rem', marginBottom: '2.5rem' }}>
            <div>
              <h4 style={{ color: '#ffffff', fontSize: '1.25rem', fontWeight: 800, marginBottom: '0.75rem' }}>
                नागरिक सेतु <span style={{ color: '#FF9933' }}>· NagrikSetu</span>
              </h4>
              <p style={{ fontSize: '0.82rem', lineHeight: 1.6, color: '#cbd5e1' }}>
                National Citizen Opportunity, Welfare & Employment Intelligence Platform. Department of Skill Development & Entrepreneurship.
              </p>
              <div style={{ marginTop: '1.25rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <a
                  href="http://localhost:5173"
                  style={{
                    color: '#FF9933',
                    fontSize: '0.82rem',
                    fontWeight: 700,
                    textDecoration: 'none',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem'
                  }}
                >
                  ← Return to NagrikSetu Central Portal (localhost:5173)
                </a>
                <a
                  href="http://localhost:5174"
                  style={{
                    color: '#94a3b8',
                    fontSize: '0.82rem',
                    fontWeight: 600,
                    textDecoration: 'none',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.4rem'
                  }}
                >
                  🎓 Access School & Education Portal (localhost:5174)
                </a>
              </div>
            </div>
            <div>
              <h5 style={{ color: '#ffffff', fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.75rem' }}>Official Navigation</h5>
              <div style={{ display: 'grid', gap: '0.4rem', fontSize: '0.82rem' }}>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('courses')}>Explore 100+ Skill Courses</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('programmes')}>Subsidized Training Programmes</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('trainers')}>Master Trainers & Faculty</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('centres')}>Accredited Training Centres</span>
              </div>
            </div>
            <div>
              <h5 style={{ color: '#ffffff', fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.75rem' }}>Citizen Services</h5>
              <div style={{ display: 'grid', gap: '0.4rem', fontSize: '0.82rem' }}>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('gap')}>Skill Gap Analysis Engine</span>
                <span style={{ cursor: 'pointer' }} onClick={() => setActiveTab('careers')}>Career & Apprenticeship Search</span>
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
