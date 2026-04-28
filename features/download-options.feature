Feature: Download options
  As a user
  I want to configure format, quality, and destination
  So that downloads match my intent

  Scenario: Format selection updates quality options
    Given the media downloader app is open
    When I select video format
    Then the quality options are "Best,1080p,720p,480p,360p"
    When I select audio format
    Then the quality options are "128 kbps,192 kbps,256 kbps,320 kbps"

  Scenario: Browse destination updates the destination input
    Given the media downloader app is open
    And browse folder returns "C:\Downloads\Media"
    When I click Browse for destination
    Then destination is "C:\Downloads\Media"

  Scenario: Start download sends selected options in the request
    Given the media downloader app is open
    And validation response for "https://example.com/video" is valid with title "Payload Video"
    And start download succeeds
    When I enter URL "https://example.com/video"
    And I select video format
    And I select quality "720p"
    And I enable transcript download
    And I set destination to "downloads\custom"
    And I start the download
    Then last start request url is "https://example.com/video"
    And last start request destination is "downloads\custom"
    And last start request downloadType is "video"
    And last start request videoQuality is "720p"
    And last start request transcriptEnabled is true
