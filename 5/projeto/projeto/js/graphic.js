var type = "line"; //Por defeito gráfico de linhas

function graphic(elemento) {
  var e = document.getElementById( "selection" );
  type = e.options[e.selectedIndex].value;
}

function draw () {
    $("#graphic").highcharts({
		chart: { type: type },
		title: { text: "Média de temperaturas" },
		xAxis: { categories: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
							  "Jul", "Ago", "Set", "Out", "Nov", "Dez"] },
		series: [{ name: "Lisboa",
				   data: [7.0, 6.9, 9.5, 14.5, 18.2, 21.5, 25.2, 26.5, 23.3, 18.3, 13.9, 9.6]
				},
				{ name: "Aveiro",
				   data: [9.0, 7.9, 8.5, 13.5, 15.2, 18.5, 20.2, 24.5, 21.3, 19.3, 15.9, 13.6]
				}]
	});
};
