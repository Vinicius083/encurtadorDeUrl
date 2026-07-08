import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators,
  AbstractControl,
  ValidationErrors,
} from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ToastService } from '../../shared/services/toast.service';
import { AuthService } from '../../shared/services/auth.service';
import { formatErrorMessage } from '../../shared/utils/error-formatter';

@Component({
  selector: 'app-cadastro',
  standalone: true,
  imports: [RouterLink, ReactiveFormsModule],
  templateUrl: './cadastro.html',
  styleUrl: './cadastro.css',
})
export class CadastroComponent {
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);
  private readonly toastService = inject(ToastService);
  private readonly authService = inject(AuthService);
  private readonly http = inject(HttpClient);

  readonly registerForm: FormGroup;
  readonly isSubmitting = signal(false);

  constructor() {
    this.registerForm = this.fb.group(
      {
        fullName: ['', [Validators.required, Validators.minLength(3)]],
        email: ['', [Validators.required, Validators.email]],
        password: ['', [Validators.required, Validators.minLength(8)]],
        confirmPassword: ['', [Validators.required]],
      },
      {
        validators: this.passwordMatchValidator,
      },
    );
  }

  private passwordMatchValidator(control: AbstractControl): ValidationErrors | null {
    const password = control.get('password')?.value;
    const confirmPassword = control.get('confirmPassword')?.value;

    if (password && confirmPassword && password !== confirmPassword) {
      control.get('confirmPassword')?.setErrors({ passwordMismatch: true });
      return { passwordMismatch: true };
    }

    const errors = control.get('confirmPassword')?.errors;
    if (errors && errors['passwordMismatch']) {
      delete errors['passwordMismatch'];
      if (Object.keys(errors).length === 0) {
        control.get('confirmPassword')?.setErrors(null);
      } else {
        control.get('confirmPassword')?.setErrors(errors);
      }
    }

    return null;
  }

  onSubmit() {
    if (this.registerForm.invalid) {
      this.registerForm.markAllAsTouched();
      this.toastService.warning(
        'Formulário Inválido',
        'Por favor, preencha todos os campos corretamente.',
      );
      return;
    }

    this.isSubmitting.set(true);
    const { fullName, email, password } = this.registerForm.value;
    const payload = { nome: fullName, email, senha: password };

    this.http.post<any>('http://localhost:8000/register', payload).subscribe({
      next: (res) => {
        this.authService.setSession(res.token, res.nome);
        this.toastService.success(
          'Cadastro Realizado',
          `Olá, ${res.nome}! Sua conta foi criada com sucesso.`,
        );
        this.router.navigate(['/home']);
        this.isSubmitting.set(false);
      },
      error: (err) => {
        const errorMsg = formatErrorMessage(err);
        this.toastService.error('Erro de Cadastro', errorMsg);
        this.isSubmitting.set(false);
      },
    });
  }
}
