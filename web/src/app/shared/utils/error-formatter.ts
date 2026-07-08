export function formatErrorMessage(err: any): string {
  if (!err) return 'Ocorreu um erro inesperado.';
  
  // Try to access the error body (Angular HttpErrorResponse maps response body to err.error)
  const errorBody = err.error || err;
  
  if (errorBody && errorBody.detail) {
    const detail = errorBody.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    
    if (Array.isArray(detail)) {
      return detail
        .map(item => {
          const field = item.loc && item.loc.length > 0 ? item.loc[item.loc.length - 1] : '';
          let msg = item.msg || '';
          
          // Translate common Pydantic validations
          if (msg.includes('String should have at least')) {
            const limit = item.ctx?.min_length || '';
            msg = `deve ter pelo menos ${limit} caracteres`;
          } else if (msg.includes('value is not a valid email address')) {
            msg = 'deve ser um e-mail válido';
          } else if (msg.includes('Field required')) {
            msg = 'é obrigatório';
          } else if (msg.includes('Input should be a valid URL')) {
            msg = 'deve ser uma URL válida';
          }
          
          if (field) {
            // Capitalize or localize common fields
            let fieldLabel = field.charAt(0).toUpperCase() + field.slice(1);
            if (field === 'senha') fieldLabel = 'Senha';
            if (field === 'nome') fieldLabel = 'Nome';
            if (field === 'url_original') fieldLabel = 'URL Original';
            
            return `• ${fieldLabel}: ${msg}`;
          }
          return `• ${msg}`;
        })
        .join('\n');
    }
  }
  
  return err.message || 'Ocorreu um erro inesperado.';
}
