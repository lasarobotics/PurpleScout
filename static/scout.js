$(document).ready(function () {
    try {
        let lastResult = localStorage.getItem('last_bet_result');
        if (lastResult) {
            lastResult = JSON.parse(lastResult);
            setTimeout(() => {
                if (lastResult.cancelled) {
                    alert("Match bets were CANCELLED by Mega Scout! Your bet of " + lastResult.payout + " has been refunded.");
                } else if (lastResult.won) {
                    alert("🎉 YOU WON YOUR BET! " + lastResult.payout + " PH Bucks have been credited to your balance! 🎉");
                } else {
                    alert("😢 Your alliance lost... " + lastResult.winner + " won the match.");
                }
            }, 500); // Slight delay ensures page renders first
            localStorage.removeItem('last_bet_result');
        }
    } catch(e) {}

    var socket = io();

    // ----------- AUTH LOGIC -------------
    $('#prediction_table').css('pointer-events', 'none').css('opacity', '0.5');

    function getAuthForBalanceSync() {
        const sid = (
            sessionStorage.getItem('scoutAuthSID_temp') ||
            $('input[name="scoutID"]').val() ||
            localStorage.getItem('acc_info') ||
            ''
        ).toString().trim();
        const pwd = (
            sessionStorage.getItem('scoutPassword_temp') ||
            $('#scoutPassword').val() ||
            ''
        ).toString();
        return { sid, pwd };
    }

    window.syncBalanceToBackend = function(newBal) {
        const parsedBal = parseInt(newBal);
        if (Number.isNaN(parsedBal)) return false;

        const { sid, pwd } = getAuthForBalanceSync();
        if (sid && pwd) {
            socket.emit('updateBalance', {scoutID: sid, password: pwd, newBalance: parsedBal});
            return true;
        }

        // Queue a retry for when auth is available again.
        localStorage.setItem('pending_balance_target', String(parsedBal));
        return false;
    };

    function tryAuth() {
        let sid = $('input[name="scoutID"]').val();
        let pwd = $('#scoutPassword').val();
        if (sid && pwd) {
            socket.emit('checkBettingAccount', {scoutID: sid, password: pwd});
        } else {
            $('#prediction_table').css('pointer-events', 'none').css('opacity', '0.5');
            $('#authStatus').text('Requires Auth vs Server').css('color', 'red');
        }
    }
    
    $('#scoutID').on('input', function() {
        $('#scoutPassword').val('');
        sessionStorage.removeItem('scoutPassword_temp');
        sessionStorage.removeItem('scoutAuthSID_temp');
        localStorage.removeItem('pending_balance_target');
        $('#prediction_table').css('pointer-events', 'none').css('opacity', '0.5');
        $('#authStatus').text('Requires Auth vs Server').css('color', 'red');
    });
    $('#authBtn').click(tryAuth);

    setTimeout(function() {
        $('#scoutPassword').val('');
    }, 150);

    socket.on('bettingAccountResponse', function(res) {
        if (res.success) {
            let balance = parseInt(res.balance);
            let sid = ($('input[name="scoutID"]').val() || '').toString().trim();
            localStorage.setItem('ph_bucks', balance);
            $('#ph_bucks').text(balance);
            $('#bet_amount').attr('max', balance);
            $('#authStatus').css('color', '#4CAF50').text('Authenticated! Server Balance: ' + balance);
            
            // Store password strictly across page transitions
            if ($('#scoutPassword').val()) {
                sessionStorage.setItem('scoutPassword_temp', $('#scoutPassword').val());
            }
            if (sid) {
                sessionStorage.setItem('scoutAuthSID_temp', sid);
            }

            // If a payout/refund update was queued while waiting for auth, sync now.
            const pendingBalance = localStorage.getItem('pending_balance_target');
            if (pendingBalance !== null) {
                const didSync = window.syncBalanceToBackend(parseInt(pendingBalance));
                if (didSync) {
                    localStorage.removeItem('pending_balance_target');
                }
            }

            // Unbind table wrappers
            $('#prediction_table').css('pointer-events', '').css('opacity', '1');
            $('#prediction_table *').css('pointer-events', '');
            
            if (localStorage.getItem('active_bet')) {
                // If there's an active bet, visually lock only the betting controls
                $('.pred-btn').css('pointer-events', 'none');
                $('#lock_bet_btn').text('🔒 Locked (Pending Match Reset)').css('background-color', '#444').css('pointer-events', 'none');
                $('#cancel_bet_btn').show();
            } else {
                $('#lock_bet_btn').text('🔒 Lock Prediction').css('background-color', '#663399').css('pointer-events', 'auto');
                $('#cancel_bet_btn').hide();
            }
        } else {
            $('#prediction_table').css('pointer-events', 'none').css('opacity', '0.5');
            $('#authStatus').css('color', 'red').text(res.message);
        }
    });
    // --------- END AUTH LOGIC -----------

    const assign = document.getElementById('preMatch');
    const waiting = document.getElementById('waiting');
    const form = document.getElementById('scoutForm');
    const team_text = $('#waiting b span');

    var selectedTeam = null;

    var teamID = $('#cookieTeamNum').text().trim();
    console.log("Team ID from cookie:", teamID);
    if (teamID != 'None' && teamID != "") {
        selectedTeamProcess(teamID);
    } else {
        console.log("No team ID cookie found, starting with no team selected.");
        team_text.text('None');
        $('.color-fade').css('background-color', '#663399');
        $('tbody tr:last-of-type').css('border-bottom-color', '#663399');
        socket.emit('scoutSelect', { type: selectedTeam, action: 'deselect' });
    }


    // Team select handler
    $('button.teamSelect').click(function () {
        selectedTeamProcess(this.id)
    });

    async function selectedTeamProcess(teamID) {

        if (!teamID) return;

        let percentage = 0;
        let pluggedIn = false;

        if (navigator.getBattery) {
            try {
                const battery = await navigator.getBattery();
                const batteryInfo = {
                    percent: battery.level * 100,
                    plugged: battery.charging,
                    chargingTime: battery.chargingTime,
                    dischargingTime: battery.dischargingTime
                };
                console.log("Battery Info:", batteryInfo.percent, batteryInfo.plugged);
                percentage = batteryInfo.percent;
                pluggedIn = batteryInfo.plugged;
            } catch (error) {
                console.warn('Battery API failed, continuing without battery info', error);
            }
        } else {
            console.warn('Battery API not supported; continuing without battery info.');
        }

        // emit scoutSelect event with the id of the button clicked
        if (teamID != 'deselect') {

            // deselect the current one, and select the new one
            socket.emit('scoutSelect', { type: selectedTeam, action: 'deselect' })
            socket.emit('scoutSelect', { type: teamID, scoutID: $('#scoutID').val(), action: 'select', batteryP: percentage, batteryPlug: pluggedIn });
            // show the waiting message
            waiting.style.display = 'block';
            team_text.text(teamID);
            selectedTeam = teamID;
            console.log(selectedTeam);

            if (teamID.includes('red')) {
                $('.color-fade').css('background-color', '#c93434');
                $('tbody tr:last-of-type').css('border-bottom-color', '#c93434');
            } else {
                $('.color-fade').css('background-color', '#333399');
                $('tbody tr:last-of-type').css('border-bottom-color', '#333399');
            }
        } else {
            // deselect: reset all values to default
            team_text.text('None');
            $('.color-fade').css('background-color', '#663399');
            $('tbody tr:last-of-type').css('border-bottom-color', '#663399');
            socket.emit('scoutSelect', { type: selectedTeam, action: 'deselect' });
        }
    }

    // When another scouter clicks a button, disable it
    socket.on('scoutSelect', function (data) {
        console.log(data);
        if (data.action == 'select') {
            $('#' + data.type).prop('disabled', true);
        } else {
            $('#' + data.type).prop('disabled', false);
        }
    });



    // When the mega scout gives the go ahead, start the match
    socket.on('scoutAssign', function (data) {
        console.log('Scouter ' + selectedTeam + ' is assigned to team ' + data[selectedTeam]);
        alert("The mega scout has started Match #" + data.matchNum + "! You are scouting " + selectedTeam + " and have been assigned to team " + data[selectedTeam] + ".");

        // update ui
        $('#teamNum').val(data[selectedTeam]);
        $('#matchNum').val(data.matchNum);
        
        // save dynamic payout multipliers generated by mega scout
        if (data.multipliers) {
            localStorage.setItem('match_multipliers', JSON.stringify(data.multipliers));
            $('#bet_amount').trigger('input'); // Update payout display if they already selected something
        }

        // scroll down to form
        document.querySelector('div.rebuiltBlock').scrollIntoView({
            behavior: 'smooth',
            block: 'center',
        });
    });

    // Listen for match reset / bet resolution
    socket.on('matchReset', function (data) {
        if (data && data.winner) {
            try {
                let active_bet = JSON.parse(localStorage.getItem('active_bet'));
                if (active_bet) {
                    if (active_bet.prediction === data.winner) {
                        let current_balance = parseInt(localStorage.getItem('ph_bucks') || 100);
                        let payout = parseInt(active_bet.expected_payout);
                        let new_balance = current_balance + payout;
                        localStorage.setItem('ph_bucks', new_balance);
                        $('#ph_bucks').text(new_balance);
                        $('#bet_amount').attr('max', new_balance);
                        if(window.syncBalanceToBackend) window.syncBalanceToBackend(new_balance);
                        
                        alert("🎉 YOU WON YOUR BET! " + payout + " PH Bucks have been credited to your balance! 🎉");
                    } else {
                        alert("😢 Your alliance lost... " + data.winner + " won the match.");
                        $('#bet_amount').attr('max', localStorage.getItem('ph_bucks') || 100);
                    }
                }
            } catch (e) {}
            localStorage.removeItem('active_bet');
        }
        
        // Reset the UI for next match seamlessly
        $('#prediction_table').css('pointer-events', 'auto');
        $('#prediction_table').css('opacity', '1');
        $('#lock_bet_btn').text('🔒 Lock Prediction');
        $('#lock_bet_btn').css('background-color', '#663399');
        $('#lock_bet_btn').css('color', 'white');
        $('#cancel_bet_btn').hide();
        $('.pred-btn').css('opacity', '1').css('filter', 'none');
        $('input[name="prediction"]').prop('checked', false);
        $('#bet_amount').val(0);
        $('#bet_display').text(0);
        $('#payout_display').text('0 Bucks');
    });

    socket.on('cancelBets', function (data) {
        try {
            let active_bet = JSON.parse(localStorage.getItem('active_bet'));
            if (active_bet && active_bet.original_bet !== undefined) {
                let current_balance = parseInt(localStorage.getItem('ph_bucks') || 100);
                current_balance += parseInt(active_bet.original_bet);
                localStorage.setItem('ph_bucks', current_balance);
                $('#ph_bucks').text(current_balance);
                $('#bet_amount').attr('max', current_balance);
                if (window.syncBalanceToBackend) window.syncBalanceToBackend(current_balance);
                alert("Match bets were CANCELLED by Mega Scout! Your bet of " + active_bet.original_bet + " has been refunded.");
            }
        } catch (e) {}

        localStorage.removeItem('active_bet');
        $('#cancel_bet_btn').hide();
        $('#prediction_table').css('pointer-events', '').css('opacity', '1');
        $('#prediction_table *').css('pointer-events', '');
        $('.pred-btn').css('pointer-events', '').css('opacity', '1').css('filter', 'none');
        $('#lock_bet_btn').text('🔒 Lock Prediction').css('background-color', '#663399').css('pointer-events', 'auto');
        $('input[name="prediction"]').prop('checked', false);
        $('#bet_amount').val(0);
        $('#bet_display').text(0);
        $('#payout_display').text('0 Bucks');
    });

    // Tooltip below 'Broken' field
    tippy('#fumbleTr', {
        content: 'Did the robot drop a piece while intaking, carrying, or attempting to score? Explain in comments.',
        placement: 'left',
        animation: 'fade',
    });
    tippy('#foulTr', {
        content: 'Did the ref point at your robot and wave a flag? Explain in comments.',
        placement: 'left',
    });
    tippy('#brokenTr', {
        content: 'Check if there was a <b>critical failure</b> (ex. broken part, frozen, or stuck piece) that rendered the robot basically useless. Explain in comments.',
        placement: 'left',
        allowHTML: true,
    });
    tippy('#mobilityTr', {
        content: 'Are the robot\'s bumpers completely across the starting line at the end of AUTO?',
        placement: 'top',
    });
    tippy('#defenseTr', {
        content: 'Did the robot cross over to the opposite side of the field and actively play contact defense? Explain in comments.',
        placement: 'top',
    });
    tippy('#info', {
        // content: document.getElementById('infoTooltip').innerHTML,
        placement: 'top',
        allowHTML: true,
        trigger: 'click',
        maxWidth: 'none',
    });

    // --- Betting & Prediction Logic ---
    let balance = localStorage.getItem('ph_bucks');
    if (balance === null) {
        balance = 100;
        localStorage.setItem('ph_bucks', balance);
    }
    balance = parseInt(balance);
    $('#ph_bucks').text(balance);
    $('#bet_amount').attr('max', balance);

    // Update slider dispaly and payout dynamically
    $('#bet_amount').on('input', function () {
        let val = parseInt($(this).val());
        $('#bet_display').text(val);

        let pred = $('input[name="prediction"]:checked').val();
        
        let mults = { Red: 2, Blue: 2, Tie: 100 };
        try {
            let saved = localStorage.getItem('match_multipliers');
            if (saved) mults = JSON.parse(saved);
        } catch(e) {}

        let multiplier = mults[pred] || 0;
        if (!pred) multiplier = 0;

        let payout = (val * multiplier).toFixed(1);
        if (payout.endsWith('.0')) payout = parseInt(payout);

        if (pred) {
            $('#payout_display').text(payout + ' Bucks (' + multiplier + 'x)');
        } else {
            $('#payout_display').text(payout + ' Bucks');
        }
    });

    // Handle Button Greying-Out
    $('input[name="prediction"]').change(function () {
        $('.pred-btn').css('opacity', '0.4').css('filter', 'grayscale(80%)');
        $(this).parent('.pred-btn').css('opacity', '1').css('filter', 'none');

        $('#bet_amount').trigger('input'); // Recalculate payout because multiplier might change
    });

    // Handle Locking the Bet
    $('#lock_bet_btn').click(function () {
        let bet = parseInt($('#bet_amount').val());
        let pred = $('input[name="prediction"]:checked').val();

        if (!pred) {
            alert('Please select an alliance to predict before locking your bet!');
            return;
        }

        // Visually lock the table to prevent changes without breaking form submission
        $('#prediction_table').css('pointer-events', 'none');
        $('#prediction_table').css('opacity', '0.7');

        $(this).text('🔒 Locked (' + bet + ' bucks on ' + pred + ')');
        $(this).css('background-color', '#444');
        $(this).css('color', 'white');

        // Deduct balance and strictly save it locally
        let new_balance = balance - bet;
        localStorage.setItem('ph_bucks', new_balance);
        $('#ph_bucks').text(new_balance);
        balance = new_balance;
        if(window.syncBalanceToBackend) window.syncBalanceToBackend(balance);
        
        let mults = { Red: 2, Blue: 2, Tie: 100 };
        try {
            let saved = localStorage.getItem('match_multipliers');
            if (saved) mults = JSON.parse(saved);
        } catch(e) {}
        let multiplier = mults[pred] || 0;
        let payoutAmount = bet * multiplier;

        localStorage.setItem('active_bet', JSON.stringify({ prediction: pred, expected_payout: payoutAmount, original_bet: bet }));
        $('#cancel_bet_btn').show();

        // The radio button and range slider are disabled visually, but will 
        // cleanly serialize and submit normally with the rest of the scouting data!
    });

});