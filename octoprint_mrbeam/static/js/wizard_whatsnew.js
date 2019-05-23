$(function() {
    function WizardWhatsnewViewModel(parameters) {
         var self = this;
         window.mrbeam.viewModels['wizardWhatsnewViewModel'] = self;

         self.settings = parameters[0];
         self.softwareChannelSelector = parameters[1];

         self.onAfterBinding = function(){
             $('#wizard_dialog div.modal-footer button.button-finish').text("Let's go!");
             $('#wizard_dialog div.modal-footer div.text-center').hide();
             if (self.is_bound()) {
                // test if bound, only then it's a what's new wizard
                 $('#wizard_dialog div.modal-header h3').text("✨ What's New ✨");

                 /**
                  * Set title labels on the left IF according variable for a german title is set.
                  */
                 for (var i=0; i<10; i++) {
                     if (window['wizard_plugin_corewizard_whatsnew_'+i+'_title_de']){
                        $('#wizard_plugin_corewizard_whatsnew_'+i+'_link a').text(window['wizard_plugin_corewizard_whatsnew_'+i+'_title_de']);
                     }
                 }
             } else{
                 // welcome wizard
             }
         };
         
         self.onWizardFinish = function(){
            let selected_channel = $('#whatsnew_software_channel_select').val();
            self.softwareChannelSelector.setChannelAsync(selected_channel, 1500);
            if (selected_channel != self.settings.settings.plugins.mrbeam.dev.software_tier()) {
                new PNotify({
                        title: "Switching Software Channel",
                        text: "This takes a view seconds...",
                        hide: true,
                        delay: 20 * 1000,
                        icon: "icon-cog icon-spin",
                    });
            }
        };

         self.is_bound = function(){
            var elem = document.getElementById(DOM_ELEMENT_TO_BIND_TO);
            return elem ? (!!ko.dataFor(elem)) : false;
         };



    }

    var DOM_ELEMENT_TO_BIND_TO = "wizard_plugin_corewizard_whatsnew_0";
    OCTOPRINT_VIEWMODELS.push([
        WizardWhatsnewViewModel,
        ['settingsViewModel', 'softwareChannelSelector'],
        "#"+DOM_ELEMENT_TO_BIND_TO
    ]);
});
