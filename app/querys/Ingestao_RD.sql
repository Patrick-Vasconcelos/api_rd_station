WITH cte_indicacao AS (
	SELECT
		exame.DataSist as DataIndicacao,
		LEFT(exame.CodPaciente, 6) as CodPaciente,
		exame.CodMedico,
		exame.Tipo,
		exame.Descr,
		exame.Indicacao

	FROM sisac.dbo.SolicExa as exame

	WHERE exame.Descr LIKE 'Fisiot%'
)

SELECT 
	CONVERT(NVARCHAR(10),indicacao.DataIndicacao, 103) AS DataIndicacao,
	paciente.Paciente,
	paciente.telefone2 as Contato,
	CASE
		WHEN paciente.Sexo = 'F' THEN 'Feminino'
		WHEN paciente.Sexo = 'M' THEN 'Masculino'
		ELSE 'Nao Informado'
	END AS Sexo,
	CONVERT(NVARCHAR(10), paciente.DataNasc, 103) AS DataNascimento,
	medico.Nome,
	indicacao.Indicacao


FROM cte_indicacao as indicacao

LEFT JOIN sisac.dbo.CadPaciente as paciente ON indicacao.CodPaciente = paciente.CodPaciente
LEFT JOIN sisac.dbo.CadMedico as medico ON indicacao.CodMedico = medico.CodMedico

 -- DATEADD(DAY, -1, CAST(GETDATE() AS DATE))
 --      AND DataIndicacao < CAST(GETDATE() AS DATE)

-- WHERE DataIndicacao = '2024-28-01'

WHERE DataIndicacao >= CAST(DATEADD(DAY, -1, GETDATE()) AS DATE) AND  DataIndicacao < CAST(GETDATE() AS DATE)
