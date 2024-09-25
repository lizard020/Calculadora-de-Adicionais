let selectedRow = null; // Variável para armazenar a linha selecionada

// Função para adicionar dados à tabela
document.getElementById('adicionarBtn').addEventListener('click', function() {
    const nome = document.getElementById('nome').value;
    const dataInicial = document.getElementById('dataInicial').value;
    const dataFinal = document.getElementById('dataFinal').value;
    const grau = document.getElementById('grau').value;

    if (!grau) {
        alert("Por favor, selecione um grau de insalubridade.");
        return;
    }

    if (selectedRow === null) {
        // Adiciona uma nova linha à tabela se não houver linha selecionada
        const tabela = document.getElementById('tabela').getElementsByTagName('tbody')[0];
        const novaLinha = tabela.insertRow();

        const celulaNome = novaLinha.insertCell(0);
        const celulaDataInicial = novaLinha.insertCell(1);
        const celulaDataFinal = novaLinha.insertCell(2);
        const celulaGrau = novaLinha.insertCell(3);

        celulaNome.innerHTML = nome;
        celulaDataInicial.innerHTML = dataInicial;
        celulaDataFinal.innerHTML = dataFinal;
        celulaGrau.innerHTML = grau;

        // Adiciona um evento de clique para selecionar a linha ao clicar
        novaLinha.addEventListener('click', function() {
            selecionarLinha(novaLinha);
        });
    } else {
        // Edita a linha selecionada
        selectedRow.cells[0].innerHTML = nome;
        selectedRow.cells[1].innerHTML = dataInicial;
        selectedRow.cells[2].innerHTML = dataFinal;
        selectedRow.cells[3].innerHTML = grau;

        selectedRow = null; // Resetar a seleção
        document.getElementById('editarBtn').disabled = true;
    }

    // Limpa o formulário após adicionar/editar os dados
    document.getElementById('form-dados').reset();
});

// Função para selecionar uma linha da tabela
function selecionarLinha(linha) {
    selectedRow = linha;

    // Preenche os campos do formulário com os dados da linha selecionada
    document.getElementById('nome').value = linha.cells[0].innerText;
    document.getElementById('dataInicial').value = linha.cells[1].innerText;
    document.getElementById('dataFinal').value = linha.cells[2].innerText;
    document.getElementById('grau').value = linha.cells[3].innerText;

    // Habilita o botão Editar
    document.getElementById('editarBtn').disabled = false;
}

// Função para enviar os dados ao backend Flask quando o botão "Calcular" for clicado
document.getElementById('calcularBtn').addEventListener('click', function() {
    const tabela = document.querySelectorAll('#tabela tbody tr');
    let trabalhadores = [];

    tabela.forEach(row => {
        const cells = row.querySelectorAll('td');
        const trabalhador = {
            nome: cells[0].innerText,
            data_inicial: cells[1].innerText,
            data_final: cells[2].innerText,
            porcentagem: parseFloat(cells[3].innerText)
        };
        trabalhadores.push(trabalhador);
    });

    // Envia os dados para o backend via POST
    fetch('/calcular', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ trabalhadores })
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            alert(result.error);
        } else {
            exibirResultado(result);
        }
    })
    .catch(error => console.error('Erro:', error));
});

// Função para exibir o resultado na interface
function exibirResultado(resultados) {
    const tabelaResultado = document.getElementById('resultado-tabela').getElementsByTagName('tbody')[0];
    tabelaResultado.innerHTML = ''; // Limpa qualquer resultado anterior

    resultados.forEach((resultado) => {
        const novaLinha = tabelaResultado.insertRow();

        const celulaNome = novaLinha.insertCell(0);
        const celulaMeses = novaLinha.insertCell(1);
        const celulaInsalubridadeReal = novaLinha.insertCell(2);
        const celulaInsalubridadeVPA = novaLinha.insertCell(3);

        celulaNome.innerHTML = resultado.Nome;
        celulaMeses.innerHTML = resultado.Meses;
        celulaInsalubridadeReal.innerHTML = resultado['Insalubridade Real'];
        celulaInsalubridadeVPA.innerHTML = resultado['Insalubridade VPA'];

        // Adiciona um evento de clique para exibir o DataFrame `porc`
        novaLinha.addEventListener('click', function() {
            exibirPorc(resultado.Nome, resultado.porc);
        });
    });
}

// Função para exibir o DataFrame `porc` quando o nome for clicado na tabela de resultados
function exibirPorc(nome, porc) {
    const porcContainer = document.getElementById('porc');
    const porcTitulo = document.getElementById('porc-titulo');
    
    // Define o título da seção com o nome do trabalhador
    porcTitulo.innerText = `Dias trabalhados por mês para: ${nome}`;

    // Limpa o conteúdo anterior
    porcContainer.innerHTML = '';

    // Gera a tabela com base no DataFrame `porc` retornado pelo backend
    const tabelaPorc = document.createElement('table');
    tabelaPorc.setAttribute('border', '1');

    // Cria o cabeçalho da tabela (adicionando o "Ano" como primeira coluna)
    const headerRow = document.createElement('tr');
    
    // Adiciona a coluna "Ano"
    const thAno = document.createElement('th');
    thAno.innerText = 'Ano';
    headerRow.appendChild(thAno);

    // Adiciona as colunas dos meses
    porc.columns.forEach(col => {
        const th = document.createElement('th');
        th.innerText = col;
        headerRow.appendChild(th);
    });
    tabelaPorc.appendChild(headerRow);

    // Preenche a tabela com os dados do DataFrame `porc`
    porc.index.forEach((indice, rowIndex) => {
        // Supondo que o índice seja uma tupla (Nome, Ano), extraímos só o ano
        const ano = indice[1]; // Extraímos o segundo valor da tupla, que é o ano

        const row = document.createElement('tr');

        // Adiciona o ano à primeira coluna
        const cellAno = document.createElement('td');
        cellAno.innerText = ano;
        row.appendChild(cellAno);

        // Preenche as demais colunas com os dados dos meses
        porc.data[rowIndex].forEach(cellData => {
            const cell = document.createElement('td');
            cell.innerText = cellData;
            row.appendChild(cell);
        });
        tabelaPorc.appendChild(row);
    });

    // Adiciona a tabela ao container
    porcContainer.appendChild(tabelaPorc);
}