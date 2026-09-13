/**
 * SkyWings - Modern Flight Booking Application
 * Client-side Interaction & Reactive Calculations
 */

document.addEventListener('DOMContentLoaded', () => {
    initDatePickers();
    initTripTypeToggle();
    initAirportAutocomplete();
    initQuickChips();
    initSwapButton();
    initFlightResultsFilter();
    initSeatMap();
    initAddonsAndPricing();
    initPaymentTabs();
    initCardPreview();
});

/* --------------------------------------------------------------------------
   1. Date Pickers Setup
   -------------------------------------------------------------------------- */
function initDatePickers() {
    const departureInput = document.getElementById('departure_date');
    const returnInput = document.getElementById('return_date');

    if (departureInput) {
        const today = new Date().toISOString().split('T')[0];
        if (!departureInput.min) departureInput.min = today;
        if (!departureInput.value) departureInput.value = today;

        departureInput.addEventListener('change', () => {
            if (returnInput) {
                returnInput.min = departureInput.value;
                if (returnInput.value && returnInput.value < departureInput.value) {
                    returnInput.value = departureInput.value;
                }
            }
        });
    }

    if (returnInput && departureInput && departureInput.value) {
        returnInput.min = departureInput.value;
    }
}

/* --------------------------------------------------------------------------
   2. Trip Type Toggle (One Way vs Round Trip)
   -------------------------------------------------------------------------- */
function initTripTypeToggle() {
    const tripRadios = document.querySelectorAll('input[name="trip_type"]');
    const returnGroup = document.getElementById('return-date-group');
    const returnInput = document.getElementById('return_date');

    if (!returnGroup) return;

    tripRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'round_trip') {
                returnGroup.style.opacity = '1';
                returnGroup.style.pointerEvents = 'auto';
                if (returnInput) returnInput.required = true;
            } else {
                returnGroup.style.opacity = '0.4';
                returnGroup.style.pointerEvents = 'none';
                if (returnInput) {
                    returnInput.required = false;
                    returnInput.value = '';
                }
            }
        });
    });
}

/* --------------------------------------------------------------------------
   3. Airport Autocomplete
   -------------------------------------------------------------------------- */
const AIRPORTS = [
    { code: 'DEL', city: 'Delhi', name: 'Indira Gandhi International Airport' },
    { code: 'BOM', city: 'Mumbai', name: 'Chhatrapati Shivaji Maharaj International Airport' },
    { code: 'BLR', city: 'Bangalore', name: 'Kempegowda International Airport' },
    { code: 'PNQ', city: 'Pune', name: 'Pune International Airport' },
    { code: 'HYD', city: 'Hyderabad', name: 'Rajiv Gandhi International Airport' },
    { code: 'MAA', city: 'Chennai', name: 'Chennai International Airport' },
    { code: 'CCU', city: 'Kolkata', name: 'Netaji Subhash Chandra Bose Intl' },
    { code: 'GOI', city: 'Goa', name: 'Dabolim / Manohar International Airport' },
    { code: 'JAI', city: 'Jaipur', name: 'Jaipur International Airport' },
    { code: 'COK', city: 'Kochi', name: 'Cochin International Airport' },
    { code: 'AMD', city: 'Ahmedabad', name: 'Sardar Vallabhbhai Patel Intl' },
    { code: 'DXB', city: 'Dubai', name: 'Dubai International Airport' },
    { code: 'SIN', city: 'Singapore', name: 'Singapore Changi Airport' },
    { code: 'LHR', city: 'London', name: 'Heathrow Airport' }
];

function initAirportAutocomplete() {
    setupAutocomplete('from_input', 'from_dropdown');
    setupAutocomplete('to_input', 'to_dropdown');
}

function setupAutocomplete(inputId, dropdownId) {
    const input = document.getElementById(inputId);
    const dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) return;

    function renderList(matches) {
        if (!matches.length) {
            dropdown.innerHTML = '<div class="autocomplete-item" style="color: #94a3b8; font-size: 0.85rem;">No matching airports found</div>';
            dropdown.style.display = 'block';
            return;
        }

        dropdown.innerHTML = matches.map(a => `
            <div class="autocomplete-item" data-code="${a.code}" data-city="${a.city}">
                <div>
                    <div class="autocomplete-city">${a.city} (${a.code})</div>
                    <div class="autocomplete-airport">${a.name}</div>
                </div>
                <span class="autocomplete-code">${a.code}</span>
            </div>
        `).join('');
        dropdown.style.display = 'block';

        dropdown.querySelectorAll('.autocomplete-item').forEach(item => {
            item.addEventListener('click', () => {
                input.value = item.dataset.city;
                dropdown.style.display = 'none';
            });
        });
    }

    input.addEventListener('focus', () => {
        renderList(AIRPORTS);
    });

    input.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            renderList(AIRPORTS);
            return;
        }
        const filtered = AIRPORTS.filter(a =>
            a.city.toLowerCase().includes(query) ||
            a.code.toLowerCase().includes(query) ||
            a.name.toLowerCase().includes(query)
        );
        renderList(filtered);
    });

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

/* --------------------------------------------------------------------------
   4. Quick Route Chips & Swap Button
   -------------------------------------------------------------------------- */
function initQuickChips() {
    const chips = document.querySelectorAll('.chip');
    const fromInput = document.getElementById('from_input');
    const toInput = document.getElementById('to_input');

    if (!chips.length || !fromInput || !toInput) return;

    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const from = chip.dataset.from;
            const to = chip.dataset.to;
            if (from && to) {
                fromInput.value = from;
                toInput.value = to;
            }
        });
    });
}

function initSwapButton() {
    const swapBtn = document.getElementById('swap_cities_btn');
    const fromInput = document.getElementById('from_input');
    const toInput = document.getElementById('to_input');

    if (!swapBtn || !fromInput || !toInput) return;

    swapBtn.addEventListener('click', () => {
        const temp = fromInput.value;
        fromInput.value = toInput.value;
        toInput.value = temp;
    });
}

/* --------------------------------------------------------------------------
   5. Flight Results Filter & Sort
   -------------------------------------------------------------------------- */
function initFlightResultsFilter() {
    const flightCards = document.querySelectorAll('.flight-card');
    if (!flightCards.length) return;

    const stopFilters = document.querySelectorAll('.filter-stop');
    const airlineFilters = document.querySelectorAll('.filter-airline');
    const priceSlider = document.getElementById('price_filter_slider');
    const priceDisplay = document.getElementById('price_filter_display');
    const timeButtons = document.querySelectorAll('.time-btn');
    const sortTabs = document.querySelectorAll('.sort-tab');
    const flightList = document.getElementById('flight_results_container');
    const noResultsMsg = document.getElementById('no_filter_results');

    let activeTimeSlot = 'all';

    function applyFilters() {
        let visibleCount = 0;

        const selectedStops = Array.from(stopFilters)
            .filter(cb => cb.checked)
            .map(cb => cb.value);

        const selectedAirlines = Array.from(airlineFilters)
            .filter(cb => cb.checked)
            .map(cb => cb.value.toLowerCase());

        const maxPrice = priceSlider ? parseInt(priceSlider.value) : Infinity;

        flightCards.forEach(card => {
            const cardStops = card.dataset.stops;
            const cardAirline = card.dataset.airline.toLowerCase();
            const cardPrice = parseInt(card.dataset.price);
            const cardDepTime = card.dataset.departure; // e.g. "08:15"
            const hour = parseInt(cardDepTime.split(':')[0]);

            let matchesStop = selectedStops.length === 0 || selectedStops.includes(cardStops);
            let matchesAirline = selectedAirlines.length === 0 || selectedAirlines.includes(cardAirline);
            let matchesPrice = cardPrice <= maxPrice;

            let matchesTime = true;
            if (activeTimeSlot === 'early_morning') matchesTime = hour < 6;
            else if (activeTimeSlot === 'morning') matchesTime = hour >= 6 && hour < 12;
            else if (activeTimeSlot === 'afternoon') matchesTime = hour >= 12 && hour < 18;
            else if (activeTimeSlot === 'evening') matchesTime = hour >= 18;

            if (matchesStop && matchesAirline && matchesPrice && matchesTime) {
                card.style.display = 'block';
                visibleCount++;
            } else {
                card.style.display = 'none';
            }
        });

        if (noResultsMsg) {
            noResultsMsg.style.display = visibleCount === 0 ? 'block' : 'none';
        }
    }

    if (stopFilters.length) {
        stopFilters.forEach(cb => cb.addEventListener('change', applyFilters));
    }
    if (airlineFilters.length) {
        airlineFilters.forEach(cb => cb.addEventListener('change', applyFilters));
    }
    if (priceSlider && priceDisplay) {
        priceSlider.addEventListener('input', (e) => {
            priceDisplay.textContent = '₹' + parseInt(e.target.value).toLocaleString('en-IN');
            applyFilters();
        });
    }
    if (timeButtons.length) {
        timeButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                timeButtons.forEach(b => b.classList.remove('active'));
                if (activeTimeSlot === btn.dataset.slot) {
                    activeTimeSlot = 'all';
                } else {
                    btn.classList.add('active');
                    activeTimeSlot = btn.dataset.slot;
                }
                applyFilters();
            });
        });
    }

    // Sorting
    if (sortTabs.length && flightList) {
        sortTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                sortTabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                const sortType = tab.dataset.sort;

                const cardsArray = Array.from(flightCards);
                cardsArray.sort((a, b) => {
                    if (sortType === 'cheapest') {
                        return parseInt(a.dataset.price) - parseInt(b.dataset.price);
                    } else if (sortType === 'fastest') {
                        return parseInt(a.dataset.duration) - parseInt(b.dataset.duration);
                    } else if (sortType === 'earliest') {
                        return a.dataset.departure.localeCompare(b.dataset.departure);
                    }
                    return 0;
                });

                cardsArray.forEach(card => flightList.appendChild(card));
            });
        });
    }

    // Reset filters
    const resetBtn = document.getElementById('reset_filters_btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            stopFilters.forEach(cb => cb.checked = false);
            airlineFilters.forEach(cb => cb.checked = false);
            timeButtons.forEach(b => b.classList.remove('active'));
            activeTimeSlot = 'all';
            if (priceSlider) {
                priceSlider.value = priceSlider.max;
                priceDisplay.textContent = '₹' + parseInt(priceSlider.max).toLocaleString('en-IN');
            }
            applyFilters();
        });
    }
}

/* --------------------------------------------------------------------------
   6. Interactive Aircraft Seat Map
   -------------------------------------------------------------------------- */
function initSeatMap() {
    const seats = document.querySelectorAll('.seat:not(.occupied)');
    const selectedSeatsInput = document.getElementById('selected_seats_input');
    const seatSummaryText = document.getElementById('selected_seat_display');
    const passengerCountElem = document.getElementById('passengers_count_val');

    if (!seats.length || !selectedSeatsInput) return;

    const maxSeats = passengerCountElem ? parseInt(passengerCountElem.value) || 1 : 1;
    let selectedSeats = [];

    // Pre-populate if already chosen
    if (selectedSeatsInput.value) {
        selectedSeats = selectedSeatsInput.value.split(',').map(s => s.trim()).filter(Boolean);
        selectedSeats.forEach(seatNo => {
            const el = document.querySelector(`.seat[data-seat="${seatNo}"]`);
            if (el) el.classList.add('selected');
        });
    }

    seats.forEach(seat => {
        seat.addEventListener('click', () => {
            const seatNo = seat.dataset.seat;
            const isExtraLegroom = seat.classList.contains('extra-legroom');

            if (seat.classList.contains('selected')) {
                // Deselect
                seat.classList.remove('selected');
                selectedSeats = selectedSeats.filter(s => s !== seatNo);
            } else {
                // Select
                if (selectedSeats.length >= maxSeats) {
                    // Remove first selection if max reached
                    const removedSeat = selectedSeats.shift();
                    const removedElem = document.querySelector(`.seat[data-seat="${removedSeat}"]`);
                    if (removedElem) removedElem.classList.remove('selected');
                }
                seat.classList.add('selected');
                selectedSeats.push(seatNo);
            }

            selectedSeatsInput.value = selectedSeats.join(', ');
            if (seatSummaryText) {
                seatSummaryText.textContent = selectedSeats.length ? selectedSeats.join(', ') : 'Not selected';
            }

            // Trigger pricing update
            window.dispatchEvent(new CustomEvent('seatSelectionChanged', { detail: { selectedSeats } }));
        });
    });
}

/* --------------------------------------------------------------------------
   7. Add-ons, Coupons, and Dynamic Price Calculation
   -------------------------------------------------------------------------- */
function initAddonsAndPricing() {
    const baseFareElem = document.getElementById('summary_base_fare');
    const taxesElem = document.getElementById('summary_taxes');
    const addonFeeElem = document.getElementById('summary_addon_fee');
    const discountRow = document.getElementById('summary_discount_row');
    const discountElem = document.getElementById('summary_discount');
    const totalElem = document.getElementById('summary_total');
    const totalInput = document.getElementById('total_price_input');

    if (!baseFareElem || !totalElem) return;

    let baseFare = parseFloat(baseFareElem.dataset.amount) || 0;
    let taxes = parseFloat(taxesElem?.dataset.amount) || 0;
    let extraSeatFee = 0;
    let mealFee = 0;
    let luggageFee = 0;
    let insuranceFee = 0;
    let discount = 0;

    // Listen to seat selection
    window.addEventListener('seatSelectionChanged', (e) => {
        const seats = e.detail.selectedSeats;
        extraSeatFee = 0;
        seats.forEach(s => {
            const seatEl = document.querySelector(`.seat[data-seat="${s}"]`);
            if (seatEl && seatEl.classList.contains('extra-legroom')) {
                extraSeatFee += 500; // Extra legroom fee ₹500
            }
        });
        updateTotals();
    });

    // Meal cards
    const mealCheckboxes = document.querySelectorAll('.addon-meal-checkbox');
    mealCheckboxes.forEach(cb => {
        cb.addEventListener('change', () => {
            mealFee = 0;
            mealCheckboxes.forEach(c => {
                if (c.checked) mealFee += parseFloat(c.dataset.price) || 0;
            });
            updateTotals();
        });
    });

    // Baggage upgrade checkbox
    const luggageCheckbox = document.getElementById('addon_luggage_checkbox');
    if (luggageCheckbox) {
        luggageCheckbox.addEventListener('change', (e) => {
            luggageFee = e.target.checked ? (parseFloat(e.target.dataset.price) || 900) : 0;
            updateTotals();
        });
    }

    // Travel Insurance checkbox
    const insuranceCheckbox = document.getElementById('addon_insurance_checkbox');
    if (insuranceCheckbox) {
        insuranceCheckbox.addEventListener('change', (e) => {
            const pCount = parseInt(document.getElementById('passengers_count_val')?.value) || 1;
            insuranceFee = e.target.checked ? ((parseFloat(e.target.dataset.price) || 199) * pCount) : 0;
            updateTotals();
        });
    }

    // Coupon Apply
    const couponInput = document.getElementById('coupon_code_input');
    const couponBtn = document.getElementById('apply_coupon_btn');
    const couponMsg = document.getElementById('coupon_message');
    const couponCodeHidden = document.getElementById('coupon_code_hidden');

    if (couponBtn && couponInput) {
        couponBtn.addEventListener('click', () => {
            const code = couponInput.value.trim().toUpperCase();
            if (!code) return;

            // Pre-defined valid coupons check
            if (code === 'FLYHIGH') {
                discount = Math.min(Math.round(baseFare * 0.15), 1200);
                showCouponSuccess(code, `₹${discount} discount applied! (15% off)`);
            } else if (code === 'SKY500') {
                discount = 500;
                showCouponSuccess(code, `₹500 flat discount applied!`);
            } else if (code === 'FIRSTFLY') {
                discount = Math.min(Math.round(baseFare * 0.20), 1500);
                showCouponSuccess(code, `₹${discount} discount applied! (20% off)`);
            } else if (code === 'FESTIVE') {
                discount = Math.min(Math.round(baseFare * 0.10), 800);
                showCouponSuccess(code, `₹${discount} discount applied! (10% off)`);
            } else {
                discount = 0;
                if (couponMsg) {
                    couponMsg.innerHTML = '<span style="color: #ef4444; font-size: 0.85rem; font-weight: 600;">Invalid or expired coupon code. Try <b>FLYHIGH</b> or <b>SKY500</b></span>';
                }
                if (couponCodeHidden) couponCodeHidden.value = '';
            }
            updateTotals();
        });
    }

    function showCouponSuccess(code, msg) {
        if (couponMsg) {
            couponMsg.innerHTML = `<span style="color: #10b981; font-size: 0.85rem; font-weight: 600;">✓ ${msg}</span>`;
        }
        if (couponCodeHidden) couponCodeHidden.value = code;
    }

    function updateTotals() {
        const totalAddon = extraSeatFee + mealFee + luggageFee + insuranceFee;
        if (addonFeeElem) {
            addonFeeElem.textContent = '₹' + totalAddon.toLocaleString('en-IN');
            const addonInput = document.getElementById('add_on_fee_input');
            if (addonInput) addonInput.value = totalAddon;
        }

        if (discount > 0 && discountRow && discountElem) {
            discountRow.style.display = 'flex';
            discountElem.textContent = '-₹' + discount.toLocaleString('en-IN');
            const discountInput = document.getElementById('discount_input');
            if (discountInput) discountInput.value = discount;
        } else if (discountRow) {
            discountRow.style.display = 'none';
        }

        const grandTotal = Math.max(0, baseFare + taxes + totalAddon - discount);
        totalElem.textContent = '₹' + grandTotal.toLocaleString('en-IN');
        if (totalInput) totalInput.value = grandTotal;
    }
}

/* --------------------------------------------------------------------------
   8. Payment Gateway Tabs & Method Selection
   -------------------------------------------------------------------------- */
function initPaymentTabs() {
    const tabBtns = document.querySelectorAll('.payment-tab-btn');
    const tabPanes = document.querySelectorAll('.payment-pane');
    const paymentMethodInput = document.getElementById('payment_method_input');
    const cardInputs = document.querySelectorAll('#card_pane input');

    if (!tabBtns.length) return;

    function setCardRequired(isRequired) {
        cardInputs.forEach(input => {
            if (isRequired) {
                input.setAttribute('required', 'required');
            } else {
                input.removeAttribute('required');
            }
        });
    }

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.style.display = 'none');

            btn.classList.add('active');
            const targetPane = document.getElementById(btn.dataset.target);
            if (targetPane) targetPane.style.display = 'block';

            const method = btn.dataset.method;
            if (paymentMethodInput) {
                paymentMethodInput.value = method;
            }

            // Only require card inputs when Card pane is active
            if (btn.dataset.target === 'card_pane') {
                setCardRequired(true);
            } else {
                setCardRequired(false);
            }
        });
    });

    // Set initial requirement based on active pane
    const activeTab = document.querySelector('.payment-tab-btn.active');
    if (activeTab && activeTab.dataset.target !== 'card_pane') {
        setCardRequired(false);
    }
}

/* --------------------------------------------------------------------------
   9. Interactive Credit Card Live Preview
   -------------------------------------------------------------------------- */
function initCardPreview() {
    const cardNumInput = document.getElementById('card_number_input');
    const cardHolderInput = document.getElementById('card_holder_input');
    const cardExpInput = document.getElementById('card_exp_input');

    const displayNum = document.getElementById('card_preview_number');
    const displayName = document.getElementById('card_preview_name');
    const displayExp = document.getElementById('card_preview_exp');
    const displayBrand = document.getElementById('card_preview_brand');

    if (!cardNumInput) return;

    // Card Number Formatter
    cardNumInput.addEventListener('input', (e) => {
        let val = e.target.value.replace(/\D/g, '').substring(0, 16);
        let formatted = val.match(/.{1,4}/g)?.join(' ') || '';
        e.target.value = formatted;

        if (displayNum) {
            displayNum.textContent = formatted || '•••• •••• •••• ••••';
        }

        // Brand detection
        if (displayBrand) {
            if (val.startsWith('4')) displayBrand.textContent = 'VISA';
            else if (val.startsWith('5')) displayBrand.textContent = 'MASTERCARD';
            else if (val.startsWith('3')) displayBrand.textContent = 'AMEX';
            else displayBrand.textContent = 'CARD';
        }
    });

    // Cardholder Name
    if (cardHolderInput && displayName) {
        cardHolderInput.addEventListener('input', (e) => {
            displayName.textContent = e.target.value.toUpperCase() || 'FULL NAME';
        });
    }

    // Expiry Date Formatter MM/YY
    if (cardExpInput && displayExp) {
        cardExpInput.addEventListener('input', (e) => {
            let val = e.target.value.replace(/\D/g, '').substring(0, 4);
            if (val.length >= 2) {
                val = val.substring(0, 2) + '/' + val.substring(2);
            }
            e.target.value = val;
            displayExp.textContent = val || 'MM/YY';
        });
    }
}
