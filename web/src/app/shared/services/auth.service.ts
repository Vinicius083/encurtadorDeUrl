import { Injectable, signal, computed } from '@angular/core';

const TOKEN_KEY = 'shortify_secure_token';
const USER_NAME_KEY = 'shortify_user_name';
const XOR_KEY = 'shortify-secret-key-obfuscator';

function obfuscate(text: string): string {
  try {
    const xor = text
      .split('')
      .map((char, index) => String.fromCharCode(char.charCodeAt(0) ^ XOR_KEY.charCodeAt(index % XOR_KEY.length)))
      .join('');
    return btoa(xor);
  } catch (e) {
    return '';
  }
}

function deobfuscate(obfuscated: string): string {
  try {
    const raw = atob(obfuscated);
    return raw
      .split('')
      .map((char, index) => String.fromCharCode(char.charCodeAt(0) ^ XOR_KEY.charCodeAt(index % XOR_KEY.length)))
      .join('');
  } catch (e) {
    return '';
  }
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private readonly tokenSignal = signal<string | null>(null);
  private readonly userNameSignal = signal<string | null>(null);

  readonly token = computed(() => this.tokenSignal());
  readonly userName = computed(() => this.userNameSignal() || 'Usuário');
  readonly isAuthenticated = computed(() => !!this.tokenSignal());

  constructor() {
    this.restoreSession();
  }

  setSession(token: string, userName: string) {
    this.tokenSignal.set(token);
    this.userNameSignal.set(userName);

    // Save to sessionStorage (automatically cleared on tab/window close)
    sessionStorage.setItem(TOKEN_KEY, obfuscate(token));
    sessionStorage.setItem(USER_NAME_KEY, userName);
  }

  getToken(): string | null {
    if (!this.tokenSignal()) {
      this.restoreSession();
    }
    return this.tokenSignal();
  }

  clearSession() {
    this.tokenSignal.set(null);
    this.userNameSignal.set(null);
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(USER_NAME_KEY);
  }

  private restoreSession() {
    const obsToken = sessionStorage.getItem(TOKEN_KEY);
    const savedName = sessionStorage.getItem(USER_NAME_KEY);

    if (obsToken) {
      const token = deobfuscate(obsToken);
      if (token) {
        this.tokenSignal.set(token);
        if (savedName) {
          this.userNameSignal.set(savedName);
        }
      } else {
        this.clearSession();
      }
    }
  }
}
