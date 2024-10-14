// app.js
document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('waveform-chart').getContext('2d');
    const waveformSelect = document.getElementById('waveform-select');
    const sampleSizeInput = document.getElementById('sample-size');
    const movingAverageToggle = document.getElementById('moving-average');
    const movingVarianceToggle = document.getElementById('moving-variance');
    const sampleDifferenceToggle = document.getElementById('sample-difference');
    const movingMaxToggle = document.getElementById('moving-max');
    const movingMinToggle = document.getElementById('moving-min');

    let chart;

    function generateWaveformA() {
        // 波形Aのデータ生成
        const data = [];
        // 0を100サンプル
        data.push(...Array(100).fill(0));
        // 0から10までのスイープ
        for (let i = 0; i < 100; i++) {
            data.push(i * 0.1);
        }
        // 定常10を50サンプル
        data.push(...Array(50).fill(10));
        // 10から0までのスイープ
        for (let i = 0; i < 50; i++) {
            data.push(10 - i * 0.2);
        }
        // 0を200サンプル
        data.push(...Array(200).fill(0));
        return data;
    }

    function generateWaveformB() {
        // 波形Bのデータ生成（ランダムウォーク）
        const data = [0];
        for (let i = 1; i < 1000; i++) {
            data.push(data[i - 1] + (Math.random() - 0.5));
        }
        return data;
    }

    function updateChart() {
        const waveform = waveformSelect.value;
        const sampleSize = parseInt(sampleSizeInput.value, 10);
        const baseData = waveform === 'A' ? generateWaveformA() : generateWaveformB();
        let processedData = [...baseData];

        // データ加工
        if (movingAverageToggle.checked) {
            processedData = applyMovingAverage(processedData, sampleSize);
        }
        if (movingVarianceToggle.checked) {
            processedData = applyMovingVariance(processedData, sampleSize);
        }
        if (sampleDifferenceToggle.checked) {
            processedData = applySampleDifference(processedData, sampleSize);
        }
        if (movingMaxToggle.checked) {
            processedData = applyMovingMax(processedData, sampleSize);
        }
        if (movingMinToggle.checked) {
            processedData = applyMovingMin(processedData, sampleSize);
        }

        if (chart) {
            chart.destroy();
        }

        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: baseData.map((_, index) => index),
                datasets: [
                    {
                        label: 'ベース波形',
                        data: baseData,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1,
                        fill: false
                    },
                    {
                        label: '加工波形',
                        data: processedData,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true
                    },
                    zoom: {
                        pan: {
                            enabled: true,
                            mode: 'x',
                            threshold: 10 // パンを開始するためのピクセル数
                        },
                        zoom: {
                            wheel: {
                                enabled: true
                            },
                            pinch: {
                                enabled: true
                            },
                            mode: 'x'
                        }
                    }
                }
            }
        });
    }

    function applyMovingAverage(data, size) {
        // 移動平均の計算
        const result = [];
        for (let i = 0; i < data.length; i++) {
            const start = Math.max(0, i - size + 1);
            const subset = data.slice(start, i + 1);
            const average = subset.reduce((a, b) => a + b, 0) / subset.length;
            result.push(average);
        }
        return result;
    }

    function applyMovingVariance(data, size) {
        // 移動分散の計算
        const result = [];
        for (let i = 0; i < data.length; i++) {
            const start = Math.max(0, i - size + 1);
            const subset = data.slice(start, i + 1);
            const mean = subset.reduce((a, b) => a + b, 0) / subset.length;
            const variance = subset.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / subset.length;
            result.push(variance);
        }
        return result;
    }

    function applySampleDifference(data, size) {
        // サンプル間差分の計算
        const result = [0];
        for (let i = 1; i < data.length; i++) {
            result.push(data[i] - data[i - 1]);
        }
        return result;
    }

    function applyMovingMax(data, size) {
        // 移動最大値の計算
        const result = [];
        for (let i = 0; i < data.length; i++) {
            const start = Math.max(0, i - size + 1);
            const subset = data.slice(start, i + 1);
            result.push(Math.max(...subset));
        }
        return result;
    }

    function applyMovingMin(data, size) {
        // 移動最小値の計算
        const result = [];
        for (let i = 0; i < data.length; i++) {
            const start = Math.max(0, i - size + 1);
            const subset = data.slice(start, i + 1);
            result.push(Math.min(...subset));
        }
        return result;
    }

    waveformSelect.addEventListener('change', updateChart);
    sampleSizeInput.addEventListener('input', updateChart);
    movingAverageToggle.addEventListener('change', updateChart);
    movingVarianceToggle.addEventListener('change', updateChart);
    sampleDifferenceToggle.addEventListener('change', updateChart);
    movingMaxToggle.addEventListener('change', updateChart);
    movingMinToggle.addEventListener('change', updateChart);

    updateChart();
});
