// src/types/index.ts

export type Role = 'admin' | 'user'

export interface AuthUser {
  id?: string
  name: string
  email: string
  role: Role
  employee_id?: string | null
}

export interface LoginResponse {
  access_token: string
  token_type:   string
  role:         Role
  name:         string
  email:        string
  employee_id:  string | null
}

export interface User {
  user_id:     string
  name:        string
  employee_id: string
  department:  string
  enrolled_at?: string
}

export interface AttendanceRecord {
  attendance_id: number
  user_id:       string
  name:          string
  employee_id:   string
  department:    string
  date:          string
  time:          string
  status:        string
}

export interface AttendanceToday {
  date:    string
  count:   number
  records: AttendanceRecord[]
}

export interface AttendanceHistory {
  total:     number
  page:      number
  page_size: number
  pages:     number
  records:   AttendanceRecord[]
}

export interface AbsentUsers {
  date:   string
  count:  number
  absent: User[]
}

export interface SystemStatus {
  camera_active:       boolean
  fps:                 number
  avg_latency_ms:      number
  total_frames:        number
  processed_frames:    number
  enrolled_users:      number
  attendance_today:    number
  recognition_active:  boolean
}

export interface AttendanceStatus {
  stable_frame_required: number
  cooldown_seconds:      number
  active_frame_counters: Record<string, number>
  users_in_cooldown:     string[]
}

export interface RecognitionEvent {
  id:          string
  status:      'success' | 'exists' | 'recognizing' | 'cooldown' | 'failed'
  message:     string
  name?:       string
  employee_id?: string
  confidence?: number
  timestamp:   Date
}

export interface AdminAccount {
  id:          string
  name:        string
  email:       string
  role:        Role
  employee_id: string | null
  is_active:   boolean
  created_at:  string
}
