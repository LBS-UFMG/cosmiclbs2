<?= $this->extend('template') ?>
<?= $this->section('conteudo') ?>
<!-- Conteúdo personalizado -->

<div id="loading">
    <div class="text-center">
        <img src="<?=base_url('/img/cocadito-loading.png')?>" width="200px"><br>
        <div class="spinner-border spinner-border-sm" role="status"></div>
        <strong class="ms-2">Loading...</strong>
    </div>
</div>

<div class="container-fluid py-5 px-5">

    <h1 class="pb-5 text-dark">Explore</h1>

    <div id="explore">
        <div class="container-fluid">
            <table id="table_explore" class="table table-striped table-hover" style="width:100%; ">
                <thead>
                    <tr class="tableheader">
                        <th class="dt-center">Gene <sup><a class="badge bg-dark" href="#" data-bs-placement="top" data-bs-toggle="tooltip" data-bs-title="Gene name">?</a></sup></th>
                        
                        <th>Total Drivers</th>
                        <th>Total non-drivers</th>
                        <th class="dt-center">Driver mutations <sup><a class="badge bg-dark" href="#" data-bs-placement="top" data-bs-toggle="tooltip" data-bs-title="Mutations classified as driver according to COSMIC">?</a></sup></th>
                        <th class="dt-center">Non-Driver mutations <sup><a class="badge bg-dark" href="#" data-bs-placement="top" data-bs-toggle="tooltip" data-bs-title="Mutations classified as Non-driver according to COSMIC">?</a></sup></th>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
        </div>
    </div>

</div>
<!-- / FIM Conteúdo personalizado -->
<?= $this->endSection() ?>


<?= $this->section('scripts') ?>
<script>
    $(() => {


        const lerDados = (arquivo) => {

            // ler arquivo usando jQuery
            $.ajax({
                url: arquivo,
                success: (dados) => {
                    dados_formatados = formatarTabela(dados)

                    plotar(dados_formatados)
                }
            });
        }

        // formatar tabela --> INÍCIO 
        const formatarTabela = (dados) => {

            let dados_tabelados = [];

            // separa as linhas
            let linhas = dados.split("\n")

            // para cada linha
            for (let linha of linhas) {

                // remove caracteres especiais 
                linha = linha.replace("\r", "")

                // separa as células
                if(linha!=""){
                    celulas = linha.split("\t")
                }
                celulas[0] = `<strong><a href="<?=base_url()?>entry/${celulas[0]}">${celulas[0]}</a></strong>`;

                // salva células
                dados_tabelados.push(celulas)
            }

            return dados_tabelados
        }
        // formatar tabela --> FIM 


        // plotando a tabela
        const plotar = (dados) => {

            console.log(dados)

            // ativar datatable
            $("#table_explore").DataTable({
                "data": dados,
                // "order": [
                //     [0, 'asc']
                // ] // ordena pela coluna 0
            })
        }

        lerDados("<?= base_url('data/list.csv') ?>");

    })

    
</script>
<?= $this->endSection() ?>

<?= $this->section('scripts') ?>

<script>
        $(()=>setTimeout(() => $('#loading').fadeOut(), 1000));

// tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
</script>
<?= $this->endSection() ?>
