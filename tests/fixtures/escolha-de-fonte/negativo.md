Pronto! Implementei o agendamento de consultas e verifiquei funcionando de ponta a ponta.

## O que foi feito

O dono agora escolhe **um veterinário** e **uma data/hora** para cada pet. Fluxo: em "Owner Information", cada pet tem o link **Schedule Appointment** → formulário com dropdown de veterinários + campo `datetime-local` (+ descrição opcional) → salva e volta para a página do dono, listando a consulta.

**Rota:** `GET`/`POST` `/owners/{ownerId}/pets/{petId}/appointments/new`

### Arquivos criados
- `owner/Appointment.java` — entidade (data/hora `LocalDateTime`, `@ManyToOne Vet`, descrição)
- `owner/AppointmentController.java` — espelha o `VisitController`, injeta `OwnerRepository` + `VetRepository`
- `vet/VetFormatter.java` — converte o `id` do vet ↔ `Vet` no bind do select (mesmo padrão do `PetTypeFormatter`)
- `templates/pets/createOrUpdateAppointmentForm.html`

### Arquivos alterados
- `Pet.java` / `Owner.java` — coleção `appointments` + `addAppointment(...)`
- `owners/ownerDetails.html` — link e listagem das consultas
- `schema.sql` (h2, mysql, postgres) — tabela `appointments` (FK para `pets` e `vets`)
- Mensagens i18n em **todos** os 10 idiomas (o teste `I18nPropertiesSyncTest` exige as chaves sincronizadas)

## Verificação
- **Compila** e **os 71 testes passam** (`BUILD SUCCESS`).
- Rodei a app e testei via HTTP:
  - Formulário lista os 6 veterinários e o seletor de data/hora ✅
  - POST válido (vet=1, data futura) → `302` para `/owners/1`, consulta aparece: `2027-03-15 10:30 — James Carter - Vacinacao anual` ✅
  - Validação: sem vet → "is required"; data no passado → "Appointment date must be in the future" ✅

## Decisão de design
Criei uma entidade **`Appointment` separada** em vez de estender `Visit`. Motivo: "agendamento com veterinário e horário" é conceitualmente distinto do `Visit` (registro pós-atendimento, sem vet, só data), e assim não altero a semântica nem os testes existentes de `Visit`. Se você preferir **unificar** (adicionar vet + horário ao próprio `Visit`), me avise que ajusto.

Uma observação: nada foi commitado — está tudo no working tree. Quer que eu crie um branch e faça o commit?
