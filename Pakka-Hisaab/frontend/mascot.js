// Pakka Hisaab Mascot Module
// Provides expressive animated guide without interfering with core functionality

const Mascot = (() => {
  let state = {
    container: null,
    character: null,
    videoElement: null,
    imageElement: null,
    currentState: 'idle', // idle, attention, success, concern, hidden
    position: 'bottom-right',
    isVisible: true,
    videoSupported: false,
    reduceMotion: false
  };

  // Initialize mascot on page load
  function init() {
    // Check for prefers-reduced-motion
    state.reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Create container
    state.container = document.createElement('div');
    state.container.className = 'mascot-container position-bottom-right';
    state.container.setAttribute('aria-hidden', 'true');
    state.container.id = 'mascot-container';

    // Create character wrapper
    state.character = document.createElement('div');
    state.character.className = 'mascot-character idle';
    state.character.id = 'mascot-character';

    state.container.appendChild(state.character);
    document.body.appendChild(state.container);

    // Try to load video first, fallback to image
    loadAssets();
  }

  // Load mascot assets (video with image fallback)
  function loadAssets() {
    const videoPath = '/static/assets/mascot/mascot.mp4';
    const imagePath = '/static/assets/mascot/mascot.png';

    // Try video first (modern browsers, lightweight)
    const video = document.createElement('video');
    video.className = 'mascot-video';
    video.muted = true;
    video.playsInline = true;
    video.loop = true;
    video.autoplay = true;

    video.onloadeddata = () => {
      state.videoElement = video;
      state.videoSupported = true;
      state.character.appendChild(video);
      applyIdleAnimation();
    };

    video.onerror = () => {
      // Fallback to image
      loadImage(imagePath);
    };

    video.src = videoPath;
  }

  // Load fallback image
  function loadImage(imagePath) {
    const img = document.createElement('img');
    img.className = 'mascot-image';
    img.alt = 'Pakka Hisaab Guide';
    
    img.onload = () => {
      state.imageElement = img;
      state.character.appendChild(img);
      applyIdleAnimation();
    };

    img.onerror = () => {
      // Both assets failed - hide mascot gracefully
      hide();
      console.warn('Mascot assets not found');
    };

    img.src = imagePath;
  }

  // Apply idle animation
  function applyIdleAnimation() {
    if (!state.character) return;
    
    state.character.classList.remove('attention', 'success', 'concern');
    state.character.classList.add('idle');
    state.currentState = 'idle';
  }

  // Show attention animation (guide toward important element)
  function showAttention() {
    if (!state.character || state.reduceMotion) return;
    
    state.character.classList.remove('idle', 'success', 'concern');
    state.character.classList.add('attention');
    state.currentState = 'attention';
    
    // Return to idle after animation
    setTimeout(applyIdleAnimation, 700);
  }

  // Show success reaction
  function showSuccess() {
    if (!state.character || state.reduceMotion) return;
    
    state.character.classList.remove('idle', 'attention', 'concern');
    state.character.classList.add('success');
    state.currentState = 'success';
    
    // Return to idle after animation
    setTimeout(applyIdleAnimation, 900);
  }

  // Show concern/surprise reaction (brief, non-intrusive)
  function showConcern() {
    if (!state.character || state.reduceMotion) return;
    
    state.character.classList.remove('idle', 'attention', 'success');
    state.character.classList.add('concern');
    state.currentState = 'concern';
    
    // Return to idle after animation
    setTimeout(applyIdleAnimation, 700);
  }

  // Reposition mascot based on viewport and content
  function reposition(targetPosition = 'bottom-right') {
    if (!state.container) return;

    // Remove all position classes
    state.container.classList.remove(
      'position-bottom-right',
      'position-bottom-left',
      'position-top-right',
      'position-top-left'
    );

    // Add new position class
    state.container.classList.add(`position-${targetPosition}`);
    state.position = targetPosition;
  }

  // Guide toward command input (subtle, non-blocking)
  function guideToCommandInput() {
    const commandInput = document.getElementById('commandInput');
    if (commandInput && state.isVisible) {
      // Move mascot to top-left when input is focused
      const isInputFocused = document.activeElement === commandInput;
      if (isInputFocused) {
        reposition('top-left');
      } else {
        reposition('bottom-right');
      }
      
      // Show attention without blocking input
      showAttention();
    }
  }

  // Guide toward payment action
  function guideToPayment() {
    const paymentPanel = document.getElementById('paymentPanel');
    if (paymentPanel && state.isVisible && !state.reduceMotion) {
      reposition('bottom-left');
      showAttention();
    }
  }

  // React to payment success
  function reactToPaymentSuccess() {
    if (state.isVisible && !state.reduceMotion) {
      showSuccess();
    }
  }

  // React to payment failure (brief, subtle)
  function reactToPaymentFailure() {
    if (state.isVisible && !state.reduceMotion) {
      showConcern();
    }
  }

  // Guide toward Judge Mode
  function guideToJudgeMode() {
    const judgeButton = document.getElementById('judgeButton');
    if (judgeButton && state.isVisible) {
      reposition('top-right');
      showAttention();
    }
  }

  // Guide toward inventory/carts
  function guideToQueue() {
    const cartsList = document.getElementById('cartList');
    if (cartsList && state.isVisible) {
      reposition('bottom-right');
      showAttention();
    }
  }

  // Hide mascot temporarily
  function hide() {
    if (!state.container) return;
    state.container.classList.add('hidden');
    state.isVisible = false;
  }

  // Show mascot
  function show() {
    if (!state.container) return;
    state.container.classList.remove('hidden');
    state.isVisible = true;
  }

  // Pause video if present
  function pauseVideo() {
    if (state.videoElement) {
      state.videoElement.pause();
    }
  }

  // Resume video if present
  function resumeVideo() {
    if (state.videoElement) {
      state.videoElement.play().catch(() => {
        // Autoplay may be blocked by browser, fallback gracefully
      });
    }
  }

  // Observe application state changes and react appropriately
  function observeAppState() {
    // Listen for command execution
    const executeButton = document.getElementById('executeButton');
    if (executeButton) {
      executeButton.addEventListener('click', () => {
        // Brief attention when executing
        if (Math.random() > 0.5) showAttention();
      });
    }

    // Listen for payment state changes
    const paymentPanel = document.getElementById('paymentPanel');
    if (paymentPanel) {
      const observer = new MutationObserver(() => {
        const outcomeElement = paymentPanel.querySelector('.outcome');
        if (outcomeElement) {
          if (outcomeElement.classList.contains('success')) {
            reactToPaymentSuccess();
          } else if (outcomeElement.classList.contains('failure')) {
            reactToPaymentFailure();
          }
        }
      });

      observer.observe(paymentPanel, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class']
      });
    }

    // Guide to input when page first loads
    setTimeout(() => {
      if (state.isVisible) {
        guideToCommandInput();
      }
    }, 800);
  }

  // Public API
  return {
    init,
    show,
    hide,
    showAttention,
    showSuccess,
    showConcern,
    applyIdleAnimation,
    reposition,
    guideToCommandInput,
    guideToPayment,
    reactToPaymentSuccess,
    reactToPaymentFailure,
    guideToJudgeMode,
    guideToQueue,
    pauseVideo,
    resumeVideo,
    getState: () => ({ ...state })
  };
})();

// Initialize mascot when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    Mascot.init();
    Mascot.observeAppState();
  });
} else {
  Mascot.init();
  Mascot.observeAppState();
}
