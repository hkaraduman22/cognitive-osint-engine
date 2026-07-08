object frmMain: TfrmMain
  Left = 0
  Top = 0
  Caption = 'Ak'#305'll'#305' OSINT Firma Rehberi - Code Freeze (v1.0)'
  ClientHeight = 700
  ClientWidth = 1000
  Color = clBtnFace
  Font.Charset = DEFAULT_CHARSET
  Font.Color = clWindowText
  Font.Height = -12
  Font.Name = 'Segoe UI'
  Font.Style = []
  Position = poScreenCenter
  OnCreate = FormCreate
  TextHeight = 15
  object edtSehir: TEdit
    Left = 16
    Top = 16
    Width = 150
    Height = 23
    TabOrder = 0
    TextHint = 'Sehir (Orn: Ankara)'
  end
  object cmbSektor: TComboBox
    Left = 180
    Top = 16
    Width = 150
    Height = 23
    TabOrder = 1
    Text = 'Sektor Seciniz'
  end
  object cmbCalisanSayisi: TComboBox
    Left = 345
    Top = 16
    Width = 120
    Height = 23
    TabOrder = 2
    Text = 'Calisan Sayisi'
  end
  object edtMinPuan: TEdit
    Left = 480
    Top = 16
    Width = 100
    Height = 23
    TabOrder = 3
    TextHint = 'Min Puan (85)'
  end
  object chkSadeceYatirimAlanlar: TCheckBox
    Left = 600
    Top = 19
    Width = 120
    Height = 17
    Caption = 'Yatirim Alanlar'
    TabOrder = 4
  end
  object btnAra: TButton
    Left = 730
    Top = 15
    Width = 100
    Height = 25
    Caption = 'Vitrin Ara'
    TabOrder = 5
    OnClick = btnAraClick
  end
  object btnTaramaBaslat: TButton
    Left = 840
    Top = 15
    Width = 140
    Height = 25
    Caption = 'OSINT Taramasi Baslat'
    TabOrder = 6
    OnClick = btnTaramaBaslatClick
  end
  object btnAnalizGetir: TButton
    Left = 16
    Top = 45
    Width = 964
    Height = 25
    Caption = 'Sektorel Dagilim Analizini Getir (Grafik)'
    TabOrder = 7
    OnClick = btnAnalizGetirClick
  end
  object dbgSonuclar: TDBGrid
    Left = 16
    Top = 80
    Width = 964
    Height = 350
    DataSource = dsSonuclar
    Options = [dgTitles, dgIndicator, dgColumnResize, dgColLines, dgRowLines, dgTabs, dgRowSelect, dgConfirmDelete, dgCancelOnExit, dgTitleClick, dgTitleHotTrack]
    TabOrder = 8
    TitleFont.Charset = DEFAULT_CHARSET
    TitleFont.Color = clWindowText
    TitleFont.Height = -12
    TitleFont.Name = 'Segoe UI'
    TitleFont.Style = []
    OnDblClick = dbgSonuclarDblClick
  end
  object mmoLoglar: TMemo
    Left = 16
    Top = 440
    Width = 473
    Height = 240
    Color = clBlack
    Font.Charset = ANSI_CHARSET
    Font.Color = clLime
    Font.Height = -12
    Font.Name = 'Consolas'
    Font.Style = []
    ParentFont = False
    ReadOnly = True
    ScrollBars = ssVertical
    TabOrder = 9
  end
  object RestClient: TRESTClient
    BaseURL = 'http://localhost:8000/api/v1'
    Params = <>
    SynchronizedEvents = False
    Left = 32
    Top = 120
  end
  object RestRequest: TRESTRequest
    Client = RestClient
    Params = <>
    Response = RestResponse
    SynchronizedEvents = False
    Left = 104
    Top = 120
  end
  object RestResponse: TRESTResponse
    Left = 184
    Top = 120
  end
  object RestAdapter: TRESTResponseDataSetAdapter
    Dataset = MemTableSonuclar
    FieldDefs = <>
    Response = RestResponse
    Left = 272
    Top = 120
  end
  object MemTableSonuclar: TFDMemTable
    FetchOptions.AssignedValues = [evMode]
    FetchOptions.Mode = fmAll
    ResourceOptions.AssignedValues = [rvSilentMode]
    ResourceOptions.SilentMode = True
    UpdateOptions.AssignedValues = [uvCheckRequired, uvAutoCommitUpdates]
    UpdateOptions.CheckRequired = False
    UpdateOptions.AutoCommitUpdates = True
    Left = 376
    Top = 120
  end
  object dsSonuclar: TDataSource
    DataSet = MemTableSonuclar
    Left = 472
    Top = 120
  end
  object RestReqStats: TRESTRequest
    Client = RestClient
    Params = <>
    Response = RestResStats
    SynchronizedEvents = False
    Left = 104
    Top = 184
  end
  object RestResStats: TRESTResponse
    Left = 184
    Top = 184
  end
end
