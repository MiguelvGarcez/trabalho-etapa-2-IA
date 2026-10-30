# Matriz de decisão e engenharia do conhecimento

A base de conhecimento está em `regras_carreiras.json`; o código não contém pesos específicos das trilhas. Cada pergunta possui uma categoria e um peso global. Cada trilha possui pesos próprios por pergunta.

## Método de pontuação
1. Cada resposta usa escala Likert de 1 a 5.
2. A intensidade é transformada para o intervalo 0 a 1 por `(resposta - 1) / 4`.
3. Pesos positivos somam evidências de afinidade. Pesos negativos representam conflitos.
4. A pontuação é normalizada e convertida em percentual.
5. Regras de penalidade são aplicadas para combinações conflitantes.
6. O fator de certeza é apresentado como percentual final dividido por 100.

A pontuação é uma heurística explicável, não uma probabilidade estatística nem avaliação psicométrica validada.

## Trilha e competências mínimas
Os requisitos de competência e os roadmaps estão na seção `tracks` do JSON. Cada competência tem um nível mínimo de referência para Júnior. Os níveis declarados são convertidos em valores numéricos e a diferença positiva é o gap.

## Tratamento de perfis ambíguos
O motor não força uma escolha binária durante a inferência. Calcula as dez trilhas, ordena por aderência e apresenta Top 3. Assim, perfis com interesses mistos podem obter recomendações próximas e justificáveis.

## Limitações e manutenção
- Pesos são hipóteses de engenharia do conhecimento e devem ser validados com profissionais e usuários.
- Certificações são sugestões e podem mudar de preço, nome ou disponibilidade.
- A referência Júnior é um modelo simplificado de competências, não um padrão universal.
- Para adicionar trilhas ou alterar pesos, edite o JSON sem modificar `engine.py`.
