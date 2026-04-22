
        (function () {
            'use strict';

            // ── Utilidades ──
            function formatNumber(value) {
                if (typeof value === 'number') {
                    return value >= 1 ? value.toLocaleString('es-CO', { maximumFractionDigits: 2 })
                        : value.toFixed(4);
                }
                return value;
            }

            function renderTable(containerId, data, columns) {
                const container = document.getElementById(containerId);
                if (!container || !data || data.length === 0) return;

                const cols = columns || Object.keys(data[0]);
                let html = '<table class="data-table"><thead><tr>';
                cols.forEach(col => {
                    const label = col.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                    html += `<th>${label}</th>`;
                });
                html += '</tr></thead><tbody>';

                data.forEach(row => {
                    html += '<tr>';
                    cols.forEach(col => {
                        html += `<td>${formatNumber(row[col])}</td>`;
                    });
                    html += '</tr>';
                });

                html += '</tbody></table>';
                container.innerHTML = html;
            }

            function showError(containerId, msg) {
                const el = document.getElementById(containerId);
                if (el) el.innerHTML = `<div class="error-msg">⚠️ ${msg}</div>`;
            }

            // ── Cargar JSON ──
            async function loadJSON(path) {
                const res = await fetch(path);
                if (!res.ok) throw new Error(`HTTP ${res.status}: ${path}`);
                return res.json();
            }

            // ── Tooltip System (JS-driven DOM elements) ──
            function setupTooltips() {
                document.querySelectorAll('.kpi-card[data-tooltip]').forEach(card => {
                    let tooltipEl = null;

                    card.addEventListener('mouseenter', function () {
                        const text = this.getAttribute('data-tooltip');
                        if (!text) return;

                        // Create tooltip DOM element
                        tooltipEl = document.createElement('div');
                        tooltipEl.className = 'tooltip-box';
                        tooltipEl.textContent = text;
                        this.appendChild(tooltipEl);

                        // Force reflow, then add visible class for animation
                        tooltipEl.offsetHeight; // trigger reflow
                        tooltipEl.classList.add('visible');
                    });

                    card.addEventListener('mouseleave', function () {
                        if (!tooltipEl) return;
                        const el = tooltipEl;
                        el.classList.remove('visible');

                        // Remove from DOM after transition ends
                        el.addEventListener('transitionend', function handler() {
                            el.removeEventListener('transitionend', handler);
                            if (el.parentNode) el.parentNode.removeChild(el);
                        });
                        tooltipEl = null;
                    });
                });
            }

            // ── KPIs ──
            async function loadKPIs() {
                try {
                    const kpis = await loadJSON('static/data/kpis.json');

                    document.getElementById('fecha-reporte').textContent = kpis.generado || '—';

                    const kpiConfig = [
                        // Row 1 (4 cards): Financial core
                        { key: 'total_fob', icon: '💵', label: 'Total FOB', tooltip: 'Dólares FOB: Precio de venta en dólares sin incluir valor de seguro y fletes.', row: 1 },
                        { key: 'total_cif', icon: '💰', label: 'Total CIF', tooltip: 'Dólares CIF: Precio de venta en dólares incluyendo valor de seguro y fletes.', row: 1 },
                        { key: 'costo_logistico', icon: '🚢', label: 'Costo Logístico', tooltip: 'Diferencia entre CIF y FOB. Representa el costo de seguro y fletes marítimos/aéreos.', row: 1 },
                        { key: 'peso_total', icon: '⚖️', label: 'Peso Total', tooltip: 'Kilogramos netos: Peso en kilogramos excluyendo empaques.', row: 1 },
                        // Row 2 (3 cards): Metadata
                        { key: 'registros', icon: '📋', label: 'Registros', tooltip: 'Número total de registros de importación en el dataset.', row: 2 },
                        { key: 'productos_unicos', icon: '📦', label: 'Productos Únicos', tooltip: 'Cantidad de partidas arancelarias únicas según el Código del Sistema Armonizado.', row: 2 },
                        { key: 'paises_origen', icon: '🌍', label: 'Países de Origen', tooltip: 'País de origen: Nombre del país de origen de las importaciones.', row: 2 },
                    ];

                    const row1 = kpiConfig.filter(k => k.row === 1);
                    const row2 = kpiConfig.filter(k => k.row === 2);

                    let html = '';

                    // Row 1: Direct grid children
                    row1.forEach(kpi => {
                        const value = kpis[kpi.key] || '—';
                        html += `
                        <div class="kpi-card" data-tooltip="${kpi.tooltip}">
                            <div class="kpi-icon">${kpi.icon}</div>
                            <div class="kpi-value">${value}</div>
                            <div class="kpi-label">${kpi.label}</div>
                        </div>`;
                    });

                    // Row 2: Wrapped in centering container
                    html += '<div class="kpi-row-bottom">';
                    row2.forEach(kpi => {
                        const value = kpis[kpi.key] || '—';
                        html += `
                        <div class="kpi-card" data-tooltip="${kpi.tooltip}">
                            <div class="kpi-icon">${kpi.icon}</div>
                            <div class="kpi-value">${value}</div>
                            <div class="kpi-label">${kpi.label}</div>
                        </div>`;
                    });
                    html += '</div>';

                    document.getElementById('kpi-grid').innerHTML = html;

                    // Initialize tooltips AFTER KPIs are rendered
                    setupTooltips();
                } catch (e) {
                    document.getElementById('kpi-grid').innerHTML =
                        '<div class="error-msg" style="grid-column:1/-1;">⚠️ No se pudieron cargar los KPIs. Asegúrate de ejecutar <code>python analisis_importaciones.py</code> primero y servir con un servidor HTTP.</div>';
                }
            }

            // ── Bloque A ──
            async function loadBloqueA() {
                try {
                    const data = await loadJSON('static/data/bloque_a_productos.json');
                    if (data.top_importados) renderTable('tabla-top-importados', data.top_importados);
                    if (data.bottom_importados) renderTable('tabla-bottom-importados', data.bottom_importados);
                    if (data.top_valiosos) renderTable('tabla-top-valiosos', data.top_valiosos);
                    if (data.bottom_valiosos) renderTable('tabla-bottom-valiosos', data.bottom_valiosos);
                    if (data.top_pesados) renderTable('tabla-top-pesados', data.top_pesados);
                    if (data.bottom_pesados) renderTable('tabla-bottom-pesados', data.bottom_pesados);
                    if (data.diamantes) renderTable('tabla-diamantes', data.diamantes);
                    if (data.arena) renderTable('tabla-arena', data.arena);
                    if (data.costo_unitario_alto) renderTable('tabla-costo-unitario-alto', data.costo_unitario_alto);
                    if (data.costo_unitario_bajo) renderTable('tabla-costo-unitario-bajo', data.costo_unitario_bajo);
                } catch (e) {
                    console.warn('Bloque A data not available:', e.message);
                }
            }

            // ── Bloque B ──
            async function loadBloqueB() {
                try {
                    const data = await loadJSON('static/data/bloque_b_categorias.json');
                    if (data.nivel_tecnologico) renderTable('tabla-nivel-tecnologico', data.nivel_tecnologico);
                    if (data.uso_economico) renderTable('tabla-uso-economico', data.uso_economico);
                } catch (e) {
                    console.warn('Bloque B data not available:', e.message);
                }
            }

            // ── Bloque C ──
            async function loadBloqueC() {
                try {
                    const data = await loadJSON('static/data/bloque_c_logistica.json');
                    if (data.mayor_impacto) renderTable('tabla-mayor-impacto', data.mayor_impacto);
                    if (data.menor_impacto) renderTable('tabla-menor-impacto', data.menor_impacto);
                } catch (e) {
                    console.warn('Bloque C data not available:', e.message);
                }
            }

            // ── Bloque D ──
            async function loadBloqueD() {
                try {
                    const data = await loadJSON('static/data/bloque_d_paises.json');
                    if (data.paises_fob) renderTable('tabla-paises-fob', data.paises_fob);
                    if (data.paises_flete_caro) renderTable('tabla-paises-flete', data.paises_flete_caro);
                } catch (e) {
                    console.warn('Bloque D data not available:', e.message);
                }
            }

            // ── Bloque E ──
            async function loadBloqueE() {
                try {
                    const data = await loadJSON('static/data/bloque_e_estrategico.json');
                    if (data.sankey_flows) renderTable('tabla-sankey', data.sankey_flows);
                    if (data.scatter_benchmarking) renderTable('tabla-scatter', data.scatter_benchmarking);
                } catch (e) {
                    console.warn('Bloque E data not available:', e.message);
                }
            }

            // ── Value Row ──
            async function loadValueRow() {
                try {
                    const vr = await loadJSON('static/data/value_row.json');
                    const grid = document.getElementById('value-row-grid');
                    if (!grid) return;

                    // Market Share card
                    const pais = vr.market_share_pais || '—';
                    const pct = vr.market_share_pct || '—';
                    const mVal = vr.market_share_valor || '';

                    // Costo Unitario CIF
                    const unitCif = vr.costo_unitario_cif || '—';

                    // Tendencia Fletes
                    const fPrimer = vr.fletes_val_primer || '—';
                    const fUltimo = vr.fletes_val_ultimo || '—';
                    const fCambio = vr.fletes_cambio_pct || '—';
                    const fTrend = vr.fletes_tendencia || 'up';
                    const fMes1 = vr.fletes_primer_mes || '?';
                    const fMes2 = vr.fletes_ultimo_mes || '?';
                    const trendClass = fTrend === 'up' ? 'trend-up' : 'trend-down';
                    const trendIcon = fTrend === 'up' ? '📈' : '📉';

                    grid.innerHTML = `
                        <div class="value-card">
                            <div class="value-card-header">
                                <div class="value-card-icon">🏆</div>
                                <div class="value-card-title">Market Share por País</div>
                            </div>
                            <div class="value-card-main">${pais}</div>
                            <div class="value-card-sub">Domina con el <strong>${pct}</strong> del CIF total<br>${mVal}</div>
                        </div>
                        <div class="value-card">
                            <div class="value-card-header">
                                <div class="value-card-icon">💲</div>
                                <div class="value-card-title">Costo Unitario CIF Global</div>
                            </div>
                            <div class="value-card-main">${unitCif}</div>
                            <div class="value-card-sub">Promedio ponderado: Total CIF ÷ Unidades totales</div>
                        </div>
                        <div class="value-card">
                            <div class="value-card-header">
                                <div class="value-card-icon">${trendIcon}</div>
                                <div class="value-card-title">Tendencia de Fletes</div>
                            </div>
                            <div class="value-card-main"><span class="${trendClass}">${fCambio}</span></div>
                            <div class="value-card-sub">Mes ${fMes1}: ${fPrimer} → Mes ${fMes2}: ${fUltimo}</div>
                        </div>
                    `;
                } catch (e) {
                    const grid = document.getElementById('value-row-grid');
                    if (grid) grid.innerHTML = '<div class="error-msg" style="grid-column:1/-1;">⚠️ No se pudieron cargar las métricas avanzadas.</div>';
                }
            }

            // ── Calculator ──
            function setupCalculator() {
                const cifInput = document.getElementById('calc-cif');
                const arancelInput = document.getElementById('calc-arancel');
                const ivaInput = document.getElementById('calc-iva');
                const resCif = document.getElementById('res-cif');
                const resArancel = document.getElementById('res-arancel');
                const resIva = document.getElementById('res-iva');
                const resTotal = document.getElementById('res-total');

                if (!cifInput || !arancelInput || !ivaInput) return;

                function formatUSD(n) {
                    return '$ ' + n.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                }

                function calculate() {
                    const cif = parseFloat(cifInput.value) || 0;
                    const arancelPct = parseFloat(arancelInput.value) || 0;
                    const ivaPct = parseFloat(ivaInput.value) || 0;

                    const arancelVal = cif * (arancelPct / 100);
                    const baseIva = cif + arancelVal;
                    const ivaVal = baseIva * (ivaPct / 100);
                    const total = cif + arancelVal + ivaVal;

                    resCif.textContent = formatUSD(cif);
                    resArancel.textContent = formatUSD(arancelVal);
                    resIva.textContent = formatUSD(ivaVal);
                    resTotal.textContent = formatUSD(total);
                }

                cifInput.addEventListener('input', calculate);
                arancelInput.addEventListener('input', calculate);
                ivaInput.addEventListener('input', calculate);
            }

            // ── Bloque F ──
            async function loadBloqueF() {
                try {
                    const data = await loadJSON('static/data/bloque_f_mapas.json');
                    if (data.mapa_paises) renderTable('tabla-mapa', data.mapa_paises);
                    if (data.carga_impositiva) renderTable('tabla-carga-impositiva', data.carga_impositiva);
                } catch (e) {
                    console.warn('Bloque F data not available:', e.message);
                }
            }

            // ── Smart Calculator ──
            let smartCalcData = null;

            async function setupSmartCalculator() {
                try {
                    smartCalcData = await loadJSON('static/data/calculadora_data.json');
                } catch (e) {
                    console.warn('Calculator data not available:', e.message);
                    return;
                }

                const sectorSelect = document.getElementById('smart-sector');
                const paisSelect = document.getElementById('smart-pais');
                const cifInput = document.getElementById('smart-cif');
                const ivaInput = document.getElementById('smart-iva');

                if (!sectorSelect || !paisSelect) return;

                // Populate selects
                sectorSelect.innerHTML = '<option value="">-- Seleccionar tipo de bien --</option>';
                smartCalcData.sectores.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s;
                    opt.textContent = s.length > 60 ? s.substring(0, 60) + '...' : s;
                    sectorSelect.appendChild(opt);
                });

                paisSelect.innerHTML = '<option value="">-- Seleccionar pa\u00eds --</option>';
                smartCalcData.paises.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p;
                    opt.textContent = p;
                    paisSelect.appendChild(opt);
                });

                // Auto-suggest CIF when sector is selected
                sectorSelect.addEventListener('change', () => {
                    const sector = sectorSelect.value;
                    if (sector && smartCalcData.sector_cif_promedio[sector]) {
                        cifInput.value = smartCalcData.sector_cif_promedio[sector];
                        cifInput.placeholder = 'Mediana CIF del sector';
                    }
                    smartCalculate();
                });

                paisSelect.addEventListener('change', smartCalculate);
                cifInput.addEventListener('input', smartCalculate);
                ivaInput.addEventListener('input', smartCalculate);

                function formatUSD(n) {
                    return '$ ' + n.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                }

                function smartCalculate() {
                    const sector = sectorSelect.value;
                    const pais = paisSelect.value;
                    const cif = parseFloat(cifInput.value) || 0;
                    const ivaPct = parseFloat(ivaInput.value) || 0;

                    const sectorPct = sector && smartCalcData.sector_impacto[sector]
                        ? smartCalcData.sector_impacto[sector] : 0;
                    const paisPct = pais && smartCalcData.pais_impacto[pais]
                        ? smartCalcData.pais_impacto[pais] : 0;

                    const costoLogSector = cif * (sectorPct / 100);
                    const costoLogPais = cif * (paisPct / 100);
                    const baseIva = cif + costoLogSector + costoLogPais;
                    const ivaVal = baseIva * (ivaPct / 100);
                    const total = baseIva + ivaVal;

                    document.getElementById('smart-res-cif').textContent = formatUSD(cif);
                    document.getElementById('smart-res-logistica-sector').textContent =
                        formatUSD(costoLogSector) + ` (${sectorPct}%)`;
                    document.getElementById('smart-res-logistica-pais').textContent =
                        formatUSD(costoLogPais) + ` (${paisPct}%)`;
                    document.getElementById('smart-res-iva').textContent = formatUSD(ivaVal);
                    document.getElementById('smart-res-total').textContent = formatUSD(total);

                    // Info panel
                    let info = '';
                    if (sector) info += `<strong>Sector:</strong> Impacto log\u00edstico mediano = ${sectorPct}%<br>`;
                    if (pais) info += `<strong>Pa\u00eds:</strong> Impacto log\u00edstico mediano = ${paisPct}%<br>`;
                    if (!sector && !pais) info = 'Selecciona un tipo de bien y pa\u00eds para ver el c\u00e1lculo.';
                    document.getElementById('smart-info').innerHTML = info || 'Datos cargados.';
                }
            }

            // ── Dashboard Overview ──
            async function loadDashboardOverview() {
                try {
                    const d = await loadJSON('static/data/dashboard_overview.json');
                    const grid = document.getElementById('dash-grid');
                    if (!grid) return;

                    const DONUT_COLORS = ['#7C3AED', '#A78BFA', '#C4B5FD', '#DDD6FE', '#EDE9FE', '#F3E8FF', '#d4d4d8'];
                    const NIVEL_COLORS = ['#7C3AED', '#8B5CF6', '#A78BFA', '#C4B5FD', '#DDD6FE'];
                    const MONTH_NAMES = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

                    function fmtUSD(n) {
                        if (n >= 1e9) return '$' + (n / 1e9).toFixed(1) + 'B';
                        if (n >= 1e6) return '$' + (n / 1e6).toFixed(1) + 'M';
                        if (n >= 1e3) return '$' + (n / 1e3).toFixed(0) + 'K';
                        return '$' + n.toLocaleString('es-CO');
                    }

                    let html = '';

                    // ── Card 1: Import Overview with Monthly Comparison ──
                    if (d.totales && d.mensual) {
                        const t = d.totales;
                        const m = d.mensual;
                        const maxVal = Math.max(...m.cif, ...m.fob);

                        // Build grouped CIF/FOB bars per month
                        let barsHtml = '';
                        m.cif.forEach((cifVal, i) => {
                            const fobVal = m.fob[i] || 0;
                            const hCif = maxVal > 0 ? (cifVal / maxVal * 100) : 0;
                            const hFob = maxVal > 0 ? (fobVal / maxVal * 100) : 0;
                            const mes = MONTH_NAMES[m.meses[i]] || m.meses[i];
                            const delta = m.deltas ? m.deltas[i] : 0;
                            const deltaClass = delta > 0 ? 'positive' : delta < 0 ? 'negative' : '';
                            const deltaStr = i > 0 ? `<span class="dash-bar-delta ${deltaClass}">${delta > 0 ? '+' : ''}${delta}%</span>` : '';

                            barsHtml += `<div class="dash-bar-group">
                                <div class="dash-bar-pair">
                                    <div class="dash-bar cif" style="height:${hCif}%" title="${mes} CIF: ${fmtUSD(cifVal)}"></div>
                                    <div class="dash-bar fob" style="height:${hFob}%" title="${mes} FOB: ${fmtUSD(fobVal)}"></div>
                                </div>
                                ${deltaStr}
                                <span class="dash-bar-label">${mes}</span>
                            </div>`;
                        });

                        // Monthly comparison table
                        let tableHtml = '<div class="dash-month-table"><table><thead><tr><th>Mes</th><th>CIF</th><th>FOB</th><th>Log\u00edstico</th><th>Registros</th><th>\u0394 CIF</th></tr></thead><tbody>';
                        m.cif.forEach((cifVal, i) => {
                            const mes = MONTH_NAMES[m.meses[i]] || m.meses[i];
                            const delta = m.deltas ? m.deltas[i] : 0;
                            const deltaClass = delta > 0 ? 'positive' : delta < 0 ? 'negative' : '';
                            const deltaLabel = i === 0 ? '\u2014' : `<span class="${deltaClass}">${delta > 0 ? '+' : ''}${delta}%</span>`;
                            tableHtml += `<tr>
                                <td><strong>${mes}</strong></td>
                                <td>${fmtUSD(cifVal)}</td>
                                <td>${fmtUSD(m.fob[i] || 0)}</td>
                                <td>${fmtUSD(m.logistico ? m.logistico[i] : 0)}</td>
                                <td>${(m.registros ? m.registros[i] : 0).toLocaleString('es-CO')}</td>
                                <td>${deltaLabel}</td>
                            </tr>`;
                        });
                        tableHtml += '</tbody></table></div>';

                        html += `
                        <div class="dash-card" style="grid-column: 1 / -1;">
                            <div class="dash-card-title">
                                Comparativa Mensual de Importaciones
                                <span class="dash-badge">CIF vs FOB</span>
                            </div>
                            <div class="dash-overview-main">
                                <div class="dash-total-block">
                                    <div class="dash-total-label">Total CIF Importado</div>
                                    <div class="dash-total-value">${fmtUSD(t.total_cif)}</div>
                                    <div class="dash-total-subtitle">${t.total_registros.toLocaleString('es-CO')} registros \u00b7 ${m.meses.length} meses</div>
                                    <div class="dash-split">
                                        <div class="dash-split-item">
                                            <span class="dash-split-dot fob"></span>
                                            <div>
                                                <div class="dash-split-val">${fmtUSD(t.total_fob)}</div>
                                                <div class="dash-split-label">FOB</div>
                                            </div>
                                        </div>
                                        <div class="dash-split-item">
                                            <span class="dash-split-dot logis"></span>
                                            <div>
                                                <div class="dash-split-val">${fmtUSD(t.total_logistico)}</div>
                                                <div class="dash-split-label">Log\u00edstico (${t.pct_logistico}%)</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="dash-bars">${barsHtml}</div>
                            </div>
                            ${tableHtml}
                        </div>`
                    }

                    // ── Card 2: Distribución por Uso Económico (donut, right, top) ──
                    if (d.uso_economico) {
                        let gradientParts = [];
                        let angle = 0;
                        const usoData = d.uso_economico.slice(0, 6);
                        usoData.forEach((u, i) => {
                            const start = angle;
                            angle += u.pct * 3.6;
                            gradientParts.push(`${DONUT_COLORS[i]} ${start}deg ${angle}deg`);
                        });
                        // Rest
                        if (angle < 360) {
                            gradientParts.push(`${DONUT_COLORS[6]} ${angle}deg 360deg`);
                        }

                        let legendHtml = '';
                        usoData.forEach((u, i) => {
                            const name = u.nombre.length > 30 ? u.nombre.substring(0, 30) + '...' : u.nombre;
                            legendHtml += `
                            <div class="dash-legend-item">
                                <span class="dash-legend-dot" style="background:${DONUT_COLORS[i]}"></span>
                                <span class="dash-legend-name">${name}</span>
                                <span class="dash-legend-pct">${u.pct}%</span>
                            </div>`;
                        });

                        html += `
                        <div class="dash-card">
                            <div class="dash-card-title">
                                Uso Econ\u00f3mico
                                <span class="dash-badge">Distribuci\u00f3n</span>
                            </div>
                            <div class="dash-donut-wrapper">
                                <div class="dash-donut" style="background:conic-gradient(${gradientParts.join(',')})">
                                    <div class="dash-donut-hole">Uso<br>Econ.</div>
                                </div>
                                <div class="dash-donut-legend">${legendHtml}</div>
                            </div>
                        </div>`;
                    }

                    // ── Card 3: Top 5 Países (left, bottom) ──
                    if (d.top_paises) {
                        const FLAGS = {
                            'China': '🇨🇳', 'Estados Unidos': '🇺🇸', 'Mexico': '🇲🇽', 'M\u00e9xico': '🇲🇽', 'Alemania': '🇩🇪',
                            'Brasil': '🇧🇷', 'Jap\u00f3n': '🇯🇵', 'Corea del Sur': '🇰🇷', 'Francia': '🇫🇷', 'Italia': '🇮🇹',
                            'India': '🇮🇳', 'Canad\u00e1': '🇨🇦', 'Espa\u00f1a': '🇪🇸', 'Chile': '🇨🇱', 'Per\u00fa': '🇵🇪',
                            'Ecuador': '🇪🇨', 'Argentina': '🇦🇷', 'Colombia': '🇨🇴', 'Tailandia': '🇹🇭',
                            'Taiwan': '🇹🇼', 'Taiw\u00e1n': '🇹🇼', 'Suiza': '🇨🇭', 'Pa\u00edses Bajos': '🇳🇱',
                            'Reino Unido': '🇬🇧', 'Turqu\u00eda': '🇹🇷', 'Vietnam': '🇻🇳'
                        };

                        let countriesHtml = '';
                        d.top_paises.forEach(p => {
                            const flag = FLAGS[p.nombre] || '🌐';
                            countriesHtml += `
                            <div class="dash-country-item">
                                <div class="dash-country-flag">${flag}</div>
                                <div class="dash-country-info">
                                    <div class="dash-country-name">${p.nombre}</div>
                                    <div class="dash-country-bar">
                                        <div class="dash-country-bar-fill" style="width:${p.pct_bar}%"></div>
                                    </div>
                                </div>
                                <div class="dash-country-val">${fmtUSD(p.cif)}</div>
                            </div>`;
                        });

                        html += `
                        <div class="dash-card">
                            <div class="dash-card-title">
                                Top Pa\u00edses Importadores
                                <span class="dash-badge">Top 5</span>
                            </div>
                            <div class="dash-country-list">${countriesHtml}</div>
                        </div>`;
                    }

                    // ── Card 4: Top 5 Productos (right, bottom) ──
                    if (d.top_productos) {
                        let prodsHtml = '';
                        d.top_productos.forEach((p, i) => {
                            prodsHtml += `
                            <div class="dash-product-item">
                                <div class="dash-product-rank">${i + 1}</div>
                                <div class="dash-product-name">${p.nombre}</div>
                                <div class="dash-product-val">${fmtUSD(p.cif)}</div>
                            </div>`;
                        });

                        html += `
                        <div class="dash-card">
                            <div class="dash-card-title">
                                Productos M\u00e1s Importados
                                <span class="dash-badge">Top 5</span>
                            </div>
                            <div class="dash-product-list">${prodsHtml}</div>
                        </div>`;
                    }

                    // ── Card 5: Nivel Tecnológico (full width) ──
                    if (d.nivel_tecnologico) {
                        let nivelHtml = '';
                        d.nivel_tecnologico.forEach((n, i) => {
                            const color = NIVEL_COLORS[i % NIVEL_COLORS.length];
                            nivelHtml += `
                            <div class="dash-nivel-item">
                                <div class="dash-nivel-header">
                                    <span class="dash-nivel-name">${n.nombre}</span>
                                    <span class="dash-nivel-pct">${n.pct}%</span>
                                </div>
                                <div class="dash-nivel-bar">
                                    <div class="dash-nivel-fill" style="width:${n.pct}%;background:${color}"></div>
                                </div>
                            </div>`;
                        });

                        html += `
                        <div class="dash-card full-width">
                            <div class="dash-card-title">
                                Nivel Tecnol\u00f3gico
                                <span class="dash-badge">Distribuci\u00f3n</span>
                            </div>
                            <div class="dash-nivel-grid">${nivelHtml}</div>
                        </div>`;
                    }

                    grid.innerHTML = html;

                } catch (e) {
                    const grid = document.getElementById('dash-grid');
                    if (grid) grid.innerHTML = '<div class="error-msg" style="grid-column:1/-1;">⚠️ Dashboard no disponible.</div>';
                    console.warn('Dashboard overview not available:', e.message);
                }
            }

            // ── Timeline Interactivo ──
            let timelineDataCache = null;

            async function setupTimelineInteractiva() {
                try {
                    const res = await loadJSON('static/data/timeline_interactivo.json');
                    timelineDataCache = res.dataset || [];
                } catch (e) {
                    console.warn('Timeline interactivo data not available:', e.message);
                    return;
                }

                const inputPartida = document.getElementById('timeline-filter-partida');
                if (!inputPartida) return;

                function getThemeColors() {
                    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
                    return {
                        bg: 'rgba(0,0,0,0)',
                        grid: isDark ? 'rgba(167, 139, 250, 0.15)' : 'rgba(124, 58, 237, 0.08)',
                        text: isDark ? '#A78BFA' : '#4c1d95',
                        line: isDark ? '#C4B5FD' : '#7C3AED'
                    };
                }

                function drawChart() {
                    const filterStr = inputPartida.value.trim().toLowerCase();
                    let filtered = timelineDataCache;

                    if (filterStr) {
                        filtered = filtered.filter(row => row.p.toLowerCase().includes(filterStr));
                    }

                    if (filtered.length === 0) {
                        document.getElementById('timeline-chart').innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-dim);">⚠️ No hay datos para la partida buscada.</div>';
                        return;
                    }

                    // Agrupar por Mes
                    const agg = {};
                    filtered.forEach(row => {
                        const m = row.m;
                        if (!agg[m]) agg[m] = { flete_total: 0, fob_total: 0, cuenta: 0 };
                        agg[m].flete_total += row.c;
                        agg[m].fob_total += row.f;
                        agg[m].cuenta += 1;
                    });

                    // Ordenar meses
                    const sortedMonths = Object.keys(agg).sort((a, b) => parseInt(a) - parseInt(b));
                    const xVals = sortedMonths.map(m => `Mes ${m}`);
                    const yValsFlete = sortedMonths.map(m => agg[m].flete_total / agg[m].cuenta); // Flete promedio
                    const hoverTexts = sortedMonths.map(m => `FOB Total: $${agg[m].fob_total.toLocaleString('es-CO')}`);

                    const colors = getThemeColors();

                    const trace = {
                        x: xVals,
                        y: yValsFlete,
                        type: 'scatter',
                        mode: 'lines+markers',
                        name: 'Costo Flete Promedio',
                        text: hoverTexts,
                        hovertemplate: '<b>%{x}</b><br>Flete Promedio: $%{y:,.2f} USD<br>%{text}<extra></extra>',
                        line: { color: colors.line, width: 3 },
                        marker: { size: 8 }
                    };

                    const layout = {
                        title: { text: "Evolución de Costos de Flete (USD)", font: { color: colors.text } },
                        paper_bgcolor: colors.bg,
                        plot_bgcolor: colors.bg,
                        hovermode: 'x unified',
                        margin: { l: 50, r: 20, t: 40, b: 40 },
                        xaxis: {
                            color: colors.text,
                            gridcolor: colors.grid,
                            rangeslider: { visible: true },
                            type: 'category'
                        },
                        yaxis: {
                            color: colors.text,
                            gridcolor: colors.grid,
                            title: 'USD',
                            tickformat: ',.0f'
                        }
                    };

                    Plotly.react('timeline-chart', [trace], layout, { responsive: true, displayModeBar: false });
                }

                inputPartida.addEventListener('input', drawChart);

                // Redraw on theme change to update colors
                const oSetItem = localStorage.setItem;
                localStorage.setItem = function (key, val) {
                    oSetItem.apply(this, arguments);
                    if (key === 'theme') {
                        setTimeout(drawChart, 50);
                    }
                };

                drawChart();
            }

            // ── Active nav on scroll ──
            function setupScrollSpy() {
                const sections = ['dashboard-overview', 'buscador-interactivo', 'kpis', 'bloque-a', 'bloque-b', 'bloque-c', 'bloque-d', 'bloque-e', 'bloque-f', 'calculadora', 'ai-auditor'];
                const links = document.querySelectorAll('.nav-link');

                window.addEventListener('scroll', () => {
                    let current = '';
                    sections.forEach(id => {
                        const el = document.getElementById(id);
                        if (el && el.getBoundingClientRect().top <= 120) {
                            current = id;
                        }
                    });
                    links.forEach(link => {
                        link.classList.toggle('active', link.getAttribute('href') === '#' + current);
                    });
                });
            }

            // ── Theme Toggle ──
            function setupThemeToggle() {
                const toggle = document.getElementById('theme-toggle');
                const html = document.documentElement;

                // Load saved preference
                const saved = localStorage.getItem('theme');
                if (saved === 'dark') {
                    html.setAttribute('data-theme', 'dark');
                    toggle.textContent = '🌙';
                }

                toggle.addEventListener('click', () => {
                    const isDark = html.getAttribute('data-theme') === 'dark';
                    if (isDark) {
                        html.removeAttribute('data-theme');
                        toggle.textContent = '☀️';
                        localStorage.setItem('theme', 'light');
                    } else {
                        html.setAttribute('data-theme', 'dark');
                        toggle.textContent = '🌙';
                        localStorage.setItem('theme', 'dark');
                    }
                });
            }

            // ── Init ──
            document.addEventListener('DOMContentLoaded', () => {
                setupThemeToggle();
                loadDashboardOverview();
                loadKPIs();
                loadValueRow();
                loadBloqueA();
                loadBloqueB();
                loadBloqueC();
                loadBloqueD();
                loadBloqueE();
                loadBloqueF();
                setupCalculator();
                loadDashboardOverview();
                setupSmartCalculator();
                setupTimelineInteractiva();
                setupAIAuditor();
                setupScrollSpy();
            });

            // ── Agente Auditor IA ──
            let riskBaselines = null;
            async function setupAIAuditor() {
                try {
                    // Cargar el JSON generado por el script de predicción en Python
                    riskBaselines = await loadJSON('risk_baselines.json');
                } catch (e) {
                    console.warn('El archivo del modelo (risk_baselines.json) no se ha generado o no está en la raíz:', e.message);
                    return;
                }

                const inputPartida = document.getElementById('ai-partida');
                const inputPeso = document.getElementById('ai-peso');
                const inputFob = document.getElementById('ai-fob');

                // Elementos de Búsqueda
                const searchBox = document.getElementById('ai-search-box');
                const searchResults = document.getElementById('ai-search-results');

                // Diccionario Local de Partidas Arancelarias 
                // (Mapeando los códigos del JSON de la IA hacia descripciones enriquecidas)
                let hsDictionary = [];

                // Extraer los códigos directamente del modelo de la IA
                const codigosEntrenados = Object.keys(riskBaselines);

                // Intenta buscar el Catálogo de Productos si existe del Dashboard
                try {
                    // Cargar Bloque A para usar sus descripciones como diccionario 
                    const dataA = await loadJSON('static/data/bloque_a_productos.json');

                    // Función para extraer todos los productos únicos y mapearlos a un posible HS code
                    const productosUnicos = new Map();

                    const arraysToScan = [
                        dataA.top_importados, dataA.bottom_importados,
                        dataA.top_valiosos, dataA.diamantes, dataA.arena
                    ];

                    arraysToScan.forEach(arr => {
                        if (!arr) return;
                        arr.forEach(item => {
                            // Hacemos un reverse lookup rústico extrayendo los primeros 4-6 chars si parece código
                            if (item['Nombre partida'] && !productosUnicos.has(item['Nombre partida'])) {
                                productosUnicos.set(item['Nombre partida'], item['Nombre partida']);
                            }
                        });
                    });

                    // Como el Python entrena sobre "Codigo partida", vamos a usar los códigos entrenados
                    // y cruzar con cualquier diccionario disponible. Si no, usamos fallback genérico.
                    hsDictionary = codigosEntrenados.map(codigo => {
                        // En la vida real, sacarías la descripción real del código. 
                        // Para propósitos UI B2B, vamos a simular la descripción asumiendo que el usuario B2B sabe.
                        return { codigo: codigo, descripcion: "Mercancía Arancelaria Especializada" };
                    });

                } catch (e) {
                    console.log("No se pudo construir diccionario avanzado. Usando base de códigos IA.");
                    hsDictionary = codigosEntrenados.map(codigo => ({ codigo: codigo, descripcion: "Bienes Generales" }));
                }

                // ── Lógica de la Barra de Búsqueda ──
                function renderizarResultados(query) {
                    query = query.toLowerCase().trim();
                    searchResults.innerHTML = '';

                    if (query.length < 2) {
                        searchResults.classList.remove('active');
                        return;
                    }

                    // Filtrado Bidireccional
                    const matches = hsDictionary.filter(item =>
                        item.codigo.toLowerCase().includes(query) ||
                        item.descripcion.toLowerCase().includes(query)
                    ).slice(0, 6); // Límite UI de 6

                    if (matches.length === 0) {
                        searchResults.innerHTML = '<div class="autocomplete-empty">⚠️ No se encontraron partidas aduaneras para: "' + query + '"</div>';
                        searchResults.classList.add('active');
                        return;
                    }

                    matches.forEach(match => {
                        const div = document.createElement('div');
                        div.className = 'autocomplete-item';

                        // Resaltar Query en Amarillo
                        const regex = new RegExp(`(${query})`, "gi");
                        const highlightCodigo = match.codigo.replace(regex, "<mark style='background:#fef08a; padding:0; color:#854d0e;'>$1</mark>");

                        // Icono dinámico según IA
                        const hasIA = riskBaselines[match.codigo] ? '🤖' : '📦';

                        div.innerHTML = `
                            <span class="autocomplete-hs">${highlightCodigo}</span>
                            <span class="autocomplete-name">${hasIA} ${match.descripcion}</span>
                        `;

                        // Autocompletado Automático
                        div.addEventListener('click', () => {
                            searchBox.value = match.codigo;
                            inputPartida.value = match.codigo;
                            searchResults.classList.remove('active');

                            // Visual feedback
                            inputPartida.style.boxShadow = '0 0 0 3px rgba(16, 185, 129, 0.3)';
                            setTimeout(() => { inputPartida.style.boxShadow = 'none'; }, 800);

                            // Disparar IA
                            evaluarRiesgo();
                        });

                        searchResults.appendChild(div);
                    });

                    searchResults.classList.add('active');
                }

                searchBox.addEventListener('input', (e) => renderizarResultados(e.target.value));

                // Ocultar si clickea afuera
                document.addEventListener('click', (e) => {
                    if (!searchBox.contains(e.target) && !searchResults.contains(e.target)) {
                        searchResults.classList.remove('active');
                    }
                });

                function formatUSD(n) {
                    return '$ ' + n.toLocaleString('es-CO', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
                }

                function evaluarRiesgo() {
                    const partida = inputPartida.value.trim();
                    const peso = parseFloat(inputPeso.value) || 0;
                    const fob = parseFloat(inputFob.value) || 0;

                    if (!partida || peso <= 0 || fob <= 0) {
                        document.getElementById('ai-alerta-box').style.background = 'var(--surface-border)';
                        document.getElementById('ai-alerta-titulo').style.color = 'var(--text-dim)';
                        document.getElementById('ai-alerta-mensaje').style.color = 'var(--text)';
                        document.getElementById('ai-alerta-mensaje').textContent = 'Ingresa los datos';
                        return;
                    }

                    const precioIngresado = fob / peso;
                    document.getElementById('ai-res-precio-kg').textContent = formatUSD(precioIngresado);

                    const modelo = riskBaselines[partida];
                    if (!modelo) {
                        document.getElementById('ai-res-media').textContent = 'No hay datos históricos para esta partida';
                        document.getElementById('ai-res-umbral').textContent = '-';
                        document.getElementById('ai-alerta-box').style.background = 'var(--surface-border)';
                        document.getElementById('ai-alerta-titulo').style.color = 'var(--text-dim)';
                        document.getElementById('ai-alerta-mensaje').style.color = 'var(--text)';
                        document.getElementById('ai-alerta-mensaje').textContent = 'Sin Modelo';
                        return;
                    }

                    document.getElementById('ai-res-media').textContent = formatUSD(modelo.precio_medio_hist_usd);
                    document.getElementById('ai-res-umbral').textContent = formatUSD(modelo.umbral_riesgo_usd);

                    // IA Mínimo Histórico
                    if (precioIngresado < modelo.umbral_riesgo_usd) {
                        // Alto riesgo alert
                        document.getElementById('ai-alerta-box').style.background = 'linear-gradient(135deg, var(--danger), #b91c1c)';
                        document.getElementById('ai-alerta-titulo').style.color = 'rgba(255,255,255,0.9)';
                        document.getElementById('ai-alerta-mensaje').style.color = '#ffffff';
                        document.getElementById('ai-alerta-mensaje').textContent = '¡BANDERA ROJA!';
                    } else {
                        // Riesgo Bajo (Precio Ok)
                        document.getElementById('ai-alerta-box').style.background = 'linear-gradient(135deg, var(--success), #059669)';
                        document.getElementById('ai-alerta-titulo').style.color = 'rgba(255,255,255,0.9)';
                        document.getElementById('ai-alerta-mensaje').style.color = '#ffffff';
                        document.getElementById('ai-alerta-mensaje').textContent = 'RIESGO BAJO';
                    }
                }

                inputPartida.addEventListener('input', evaluarRiesgo);
                inputPeso.addEventListener('input', evaluarRiesgo);
                inputFob.addEventListener('input', evaluarRiesgo);
            }
        })();
    