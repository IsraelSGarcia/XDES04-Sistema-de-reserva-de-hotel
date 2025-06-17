# Calendário de Disponibilidade - RESTEL

## Visão Geral

Foi implementada uma funcionalidade de **calendário visual de disponibilidade** que mostra claramente quais dias estão disponíveis ou ocupados para cada quarto durante o processo de reserva.

## Funcionalidades Implementadas

### 1. API de Disponibilidade
- **Endpoint**: `/api/disponibilidade/<quarto_id>`
- **Método**: GET
- **Retorno**: JSON com períodos ocupados do quarto
- **Exemplo de resposta**:
```json
{
  "periodos_ocupados": [
    {
      "start": "2025-06-19",
      "end": "2025-06-26"
    },
    {
      "start": "2025-06-26", 
      "end": "2025-06-27"
    }
  ]
}
```

### 2. Interface Visual do Calendário

#### Cores e Legendas:
- 🟢 **Verde (Disponível)**: Dias livres para reserva
- 🔴 **Vermelho (Ocupado)**: Dias com reservas ativas ou check-in
- 🔵 **Azul (Selecionado)**: Período escolhido pelo usuário
- ⚪ **Cinza (Passado)**: Datas anteriores ao dia atual (desabilitadas)

#### Interatividade:
- **Clique simples**: Seleciona data de check-in
- **Segundo clique**: Seleciona data de check-out
- **Validação automática**: Impede seleção de períodos com conflitos
- **Atualização em tempo real**: Campos de data sincronizados com calendário

### 3. Páginas Implementadas

#### Hóspede - Nova Reserva
- **Arquivo**: `hospede_reserva_nova.html`
- **Localização**: Área do hóspede logado
- **Funcionalidades**:
  - Calendário visual de 3 meses
  - Seleção interativa de datas
  - Cálculo automático do valor total
  - Validação de capacidade do quarto

#### Admin - Cadastrar Reserva  
- **Arquivo**: `admin_reserva_cadastro.html`
- **Localização**: Área administrativa
- **Funcionalidades**:
  - Mesmo calendário visual
  - Funcionalidades administrativas adicionais
  - Interface diferenciada (cores amarelas)

## Tecnologias Utilizadas

### Backend (Python/Flask)
```python
@app.route('/api/disponibilidade/<int:quarto_id>')
def api_disponibilidade_quarto(quarto_id):
    # Busca reservas ativas do quarto
    # Retorna períodos ocupados em JSON
```

### Frontend (JavaScript)
- **Geração dinâmica**: Calendário criado via JavaScript
- **AJAX**: Comunicação assíncrona com API
- **Validação**: Verificação de conflitos em tempo real
- **UX**: Animações e feedback visual

### Estilos (CSS)
- **Arquivo**: `static/css/calendario.css`
- **Responsivo**: Adaptável a diferentes telas
- **Animações**: Hover effects e transições suaves
- **Acessibilidade**: Cores contrastantes e indicadores visuais

## Como Usar

### Para Hóspedes:
1. Faça login como hóspede
2. Acesse "Nova Reserva"
3. Selecione um quarto
4. O calendário aparecerá automaticamente
5. Clique nas datas disponíveis (verdes)
6. Primeira data = Check-in, Segunda data = Check-out
7. Valores são calculados automaticamente

### Para Administradores:
1. Faça login como admin
2. Acesse "Gerenciar Reservas" → "Cadastrar Nova Reserva"
3. Selecione hóspede e quarto
4. Use o calendário para visualizar disponibilidade
5. Selecione datas válidas
6. Confirme a reserva

## Validações Implementadas

### 1. Validação de Datas
- ✅ Check-in não pode ser no passado
- ✅ Check-out deve ser posterior ao check-in
- ✅ Não permite seleção de dias ocupados
- ✅ Verifica conflitos com reservas existentes

### 2. Validação de Conflitos
```javascript
function verificarConflito(inicio, fim) {
    return periodosOcupados.some(periodo => {
        return !(fim <= periodo.start || inicio >= periodo.end);
    });
}
```

### 3. Validação de Capacidade
- ✅ Número de hóspedes ≤ Capacidade do quarto
- ✅ Alerta visual quando excede limite

## Benefícios da Implementação

### Para Usuários:
- 🎯 **Clareza visual**: Vê imediatamente quais dias estão livres
- ⚡ **Rapidez**: Seleção intuitiva de datas
- 🚫 **Prevenção de erros**: Não consegue selecionar dias ocupados
- 💰 **Transparência**: Cálculo automático do valor

### Para o Sistema:
- 🔒 **Redução de conflitos**: Validação em tempo real
- 📊 **Melhor UX**: Interface mais profissional
- 🔧 **Manutenibilidade**: Código organizado e documentado
- 📱 **Responsividade**: Funciona em mobile e desktop

## Estrutura de Arquivos

```
src/restel/
├── app.py                              # API de disponibilidade
├── templates/
│   ├── hospede_reserva_nova.html      # Calendário para hóspedes
│   └── admin_reserva_cadastro.html    # Calendário para admins
static/
└── css/
    └── calendario.css                  # Estilos do calendário
```

## Próximas Melhorias Sugeridas

1. **Cache de API**: Implementar cache para melhorar performance
2. **Navegação de meses**: Botões para navegar entre meses
3. **Tooltips**: Informações detalhadas ao passar mouse
4. **Reservas parciais**: Suporte a check-in/out no meio do dia
5. **Notificações**: Alertas quando datas ficam disponíveis
6. **Integração mobile**: PWA para uso em celulares

## Testes Recomendados

### Cenários de Teste:
1. ✅ Selecionar datas disponíveis
2. ✅ Tentar selecionar datas ocupadas (deve bloquear)
3. ✅ Selecionar período que conflita parcialmente
4. ✅ Verificar cálculo automático de valores
5. ✅ Testar responsividade em mobile
6. ✅ Validar API com diferentes quartos
7. ✅ Testar com banco de dados vazio
8. ✅ Verificar comportamento com muitas reservas

## Conclusão

A funcionalidade de **calendário de disponibilidade** melhora significativamente a experiência do usuário no sistema RESTEL, fornecendo:

- **Visualização clara** da disponibilidade
- **Interação intuitiva** para seleção de datas  
- **Validação robusta** contra conflitos
- **Interface moderna** e responsiva

O sistema agora oferece uma experiência de reserva comparável aos melhores sites de hotelaria do mercado. 