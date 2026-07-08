import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ToastService } from '../../shared/services/toast.service';
import { AuthService } from '../../shared/services/auth.service';
import { formatErrorMessage } from '../../shared/utils/error-formatter';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [RouterLink, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class LoginComponent {
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);
  private readonly toastService = inject(ToastService);
  private readonly authService = inject(AuthService);
  private readonly http = inject(HttpClient);

  readonly loginForm: FormGroup;
  readonly isSubmitting = signal(false);

  constructor() {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  onSubmit() {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      this.toastService.warning('Formulário Inválido', 'Por favor, corrija os erros nos campos.');
      return;
    }

    this.isSubmitting.set(true);
    const { email, password } = this.loginForm.value;

    this.http.post<any>('http://localhost:8000/login', { email, senha: password }).subscribe({
      next: (res) => {
        this.authService.setSession(res.token, res.nome);
        this.toastService.success('Login Realizado', `Bem-vindo de volta, ${res.nome}!`);
        this.router.navigate(['/home']);
        this.isSubmitting.set(false);
      },
      error: (err) => {
        const errorMsg = formatErrorMessage(err);
        this.toastService.error('Falha na Autenticação', errorMsg);
        this.isSubmitting.set(false);
      }
    });
  }
}
