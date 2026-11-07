const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function extractErrorMessage(data: any, fallback: string): string {
    const detail = data?.detail;
    if (typeof detail === 'string') return detail;

    if (Array.isArray(detail)) {
        return detail.map((d: any) => d?.msg ?? JSON.stringify(d)).join('; ');
    }
    return fallback;
}

async function request(path: string, options: RequestInit={}){
    const res = await fetch(`${API_URL}${path}`,{
        ...options,
        credentials: 'include',
        headers: {'Content-Type': 'application/json', ...options.headers},
    });
    const data = await res.json().catch(() => null);
    if (!res.ok){
        throw new Error(extractErrorMessage(data, 'Request failed'))
    }
    return data;
}

export function register(email: string, password: string, firstName?: string, lastName?: string, phoneNumber?: string){
    return request('/auth/register',{
        method: 'POST',
        body: JSON.stringify({email,password,first_name: firstName,last_name: lastName,phone_number: phoneNumber}),
    });
}

export function login(email: string, password: string){
    return request('/auth/login',{
        method: 'POST',
        body: JSON.stringify({email,password}),
    });
}

let refreshInFlight: Promise<any> | null = null;

export function refresh() {
  if (refreshInFlight) {
    return refreshInFlight;
  }
  refreshInFlight = request('/auth/refresh', { method: 'POST' }).finally(() => {
    refreshInFlight = null;
  });
  return refreshInFlight;
}

export function logout() {
  return request('/auth/logout', { method: 'POST' });
}

export function me(accessToken: string) {
  return request('/auth/me', { headers: { Authorization: `Bearer ${accessToken}` } });
}

export function verifyEmail(token: string) {
  return request(`/auth/verify-email?token=${encodeURIComponent(token)}`);
}

export function forgotPassword(email: string) {
  return request('/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

export function resetPassword(token: string, newPassword: string) {
  return request('/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}