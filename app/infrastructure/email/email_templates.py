from typing import Dict, Any
from jinja2 import Template


TEMPLATES = {
    "verify_email": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
            .header { text-align: center; color: #333; margin-bottom: 20px; }
            .button { display: inline-block; background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; margin: 20px 0; }
            .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Bem-vindo ao Video Processing System!</h1>
            </div>
            
            <p>Olá {{ user_name }},</p>
            
            <p>Obrigado por se cadastrar! Para completar o seu registro, clique no link abaixo para verificar seu email:</p>
            
            <center>
                <a href="{{ verification_link }}" class="button">Verificar Email</a>
            </center>
            
            <p>Ou copie e cole este link no seu navegador:</p>
            <p><code>{{ verification_link }}</code></p>
            
            <p>Este link expira em 24 horas.</p>
            
            <p>Se você não criou uma conta, ignore este email.</p>
        </div>
    </body>
    </html>
    """,
    
    "password_reset": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
            .header { text-align: center; color: #333; margin-bottom: 20px; }
            .button { display: inline-block; background-color: #dc3545; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; margin: 20px 0; }
            .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Redefinição de Senha</h1>
            </div>
            
            <p>Olá {{ user_name }},</p>
            
            <p>Recebemos uma solicitação para redefinir sua senha. Clique no link abaixo:</p>
            
            <center>
                <a href="{{ reset_link }}" class="button">Redefinir Senha</a>
            </center>
            
            <p>Este link expira em 1 hora.</p>
            
            <p>Se você não solicitou isso, ignore este email.</p>
        </div>
    </body>
    </html>
    """,
    
    "job_completed": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
            .header { text-align: center; color: #333; margin-bottom: 20px; }
            .success { color: #28a745; font-size: 18px; font-weight: bold; }
            .button { display: inline-block; background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; margin: 20px 0; }
            .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Vídeo Processado com Sucesso!</h1>
            </div>
            
            <p>Olá {{ user_name }},</p>
            
            <p><span class="success">✓ Seu vídeo foi processado com sucesso!</span></p>
            
            <p><strong>Detalhes do Job:</strong></p>
            <ul>
                <li><strong>Job ID:</strong> {{ job_id }}</li>
                <li><strong>Vídeo:</strong> {{ video_name }}</li>
                <li><strong>Duração do Processamento:</strong> {{ processing_time }}</li>
            </ul>
            
            <p>Seu vídeo agora está disponível. Clique abaixo para visualizar:</p>
            
            <center>
                <a href="{{ video_link }}" class="button">Ver Vídeo</a>
            </center>
        </div>
    </body>
    </html>
    """,
    
    "job_failed": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
            .header { text-align: center; color: #333; margin-bottom: 20px; }
            .error { color: #dc3545; font-size: 18px; font-weight: bold; }
            .button { display: inline-block; background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; margin: 20px 0; }
            .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Falha no Processamento</h1>
            </div>
            
            <p>Olá {{ user_name }},</p>
            
            <p><span class="error">✗ Desculpe, houve um erro ao processar seu vídeo.</span></p>
            
            <p><strong>Detalhes do Job:</strong></p>
            <ul>
                <li><strong>Job ID:</strong> {{ job_id }}</li>
                <li><strong>Vídeo:</strong> {{ video_name }}</li>
                <li><strong>Motivo da Falha:</strong> {{ error_reason }}</li>
            </ul>
            
            <p>Por favor, tente novamente ou entre em contato com o suporte.</p>
            
            <center>
                <a href="{{ support_link }}" class="button">Contactar Suporte</a>
            </center>
        </div>
    </body>
    </html>
    """,
    
    "welcome": """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; background-color: #f5f5f5; }
            .container { max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; }
            .header { text-align: center; color: #333; margin-bottom: 20px; }
            .button { display: inline-block; background-color: #007bff; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; margin: 20px 0; }
            .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Bem-vindo ao Video Processing System!</h1>
            </div>
            
            <p>Olá {{ user_name }},</p>
            
            <p>É um prazer tê-lo conosco! Você agora pode:</p>
            
            <ul>
                <li>✓ Fazer upload e processar vídeos</li>
                <li>✓ Acompanhar o status do processamento em tempo real</li>
                <li>✓ Acessar seus vídeos processados</li>
                <li>✓ Gerenciar seus arquivos</li>
            </ul>
            
            <p>Vamos começar? Clique abaixo para acessar sua conta:</p>
            
            <center>
                <a href="{{ login_link }}" class="button">Acessar Minha Conta</a>
            </center>
            
            <p>Se tiver dúvidas, verifique nossa documentação ou entre em contato com o suporte.</p>
        </div>
    </body>
    </html>
    """,
}


def get_email_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Get and render an email template with context.
    
    Args:
        template_name: Name of the template
        context: Variables to render in template
        
    Returns:
        str: Rendered HTML content
        
    Raises:
        ValueError: If template not found
    """
    if template_name not in TEMPLATES:
        raise ValueError(
            f"Template '{template_name}' not found. "
            f"Available: {', '.join(TEMPLATES.keys())}"
        )
    
    template_content = TEMPLATES[template_name]
    template = Template(template_content)
    return template.render(**context)
