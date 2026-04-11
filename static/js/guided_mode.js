let currentStep = 0;
const totalSteps = steps.length;

const timerValue = document.getElementById('timer-value')

function showStep(index) {
    const step = steps[index];
    const nextStepText = index < totalSteps - 1 ? `Next: Step ${index + 2} <br> ${steps[index + 1].description.substring(0, 50)}...`
    : "This is the last step!";
    document.getElementById('step-title').textContent = `Step ${index + 1} of ${totalSteps}`;
    document.getElementById('step-description').textContent = step.description;
    document.getElementById('next-step-desc').innerHTML = nextStepText;

    
    const timerDiv = document.getElementById('step-timer');
    if (step.timer) {
        timerValue.textContent = step.timer;
        timerDiv.classList.remove('hidden');
    } else {
        timerDiv.classList.add('hidden');
    }
}

showStep(currentStep);

document.getElementById('prev-step').addEventListener('click', () => {
    if (currentStep > 0) {
        currentStep--;
        showStep(currentStep);
        document.getElementById('next-step').disabled = false;
        if (currentStep === 0) {
            document.getElementById('prev-step').disabled = true;
        }
    }
});

document.getElementById('next-step').addEventListener('click', () => {
    if (currentStep < totalSteps - 1) {
        currentStep++;
        showStep(currentStep);
        document.getElementById('prev-step').disabled = false;
        if (currentStep === totalSteps - 1) {
            document.getElementById('next-step').disabled = true;
        }
    }
});

let timerInterval = null;
let timeInSeconds = timerValue ? parseInt(timerValue.textContent) * 60 : 0;

const startBtn = document.getElementById('start-timer');
const pauseBtn = document.getElementById('pause-timer');
const resetBtn = document.getElementById('reset-timer');

startBtn.addEventListener('click', () => {
    const step = steps[currentStep];
    if (!step.timer || timerInterval) return;
    
    timerInterval = setInterval(() => {
        if (!timerValue) return;
        let time = parseInt(timeInSeconds);
        if (time > 0) {
            time--; 
            timeInSeconds = time;
            const minutes = Math.floor(time / 60);
            const seconds = time % 60;
            timerValue.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        } else {
            clearInterval(timerInterval);
            timerInterval = null;
        }
    }, 1000);
});

pauseBtn.addEventListener('click', () => {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
});

resetBtn.addEventListener('click', () => {
    const step = steps[currentStep];
    if (!step.timer) return;
    timerValue.textContent = step.timer;
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
});