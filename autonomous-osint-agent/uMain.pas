unit uMain;

interface

uses
  Winapi.Windows, Winapi.Messages, System.SysUtils, System.Variants, System.Classes, Vcl.Graphics,
  Vcl.Controls, Vcl.Forms, Vcl.Dialogs, REST.Types, FireDAC.Stan.Intf,
  FireDAC.Stan.Option, FireDAC.Stan.Param, FireDAC.Stan.Error, FireDAC.DatS,
  FireDAC.Phys.Intf, FireDAC.DApt.Intf, Data.DB, FireDAC.Comp.DataSet,
  FireDAC.Comp.Client, REST.Response.Adapter, REST.Client, Data.Bind.Components,
  Data.Bind.ObjectScope, Vcl.Grids, Vcl.DBGrids, Vcl.StdCtrls,
  System.Threading; // Asenkron işlemler için 2. gün eklemiştik

type
  TfrmMain = class(TForm)
    // --- 1. Gün Bileşenleri ---
    edtSehir: TEdit;
    cmbSektor: TComboBox;
    btnAra: TButton;
    dbgSonuclar: TDBGrid;
    RestClient: TRESTClient;
    RestRequest: TRESTRequest;
    RestResponse: TRESTResponse;
    RestAdapter: TRESTResponseDataSetAdapter;
    MemTableSonuclar: TFDMemTable;
    dsSonuclar: TDataSource;

    // --- 2. Gün Bileşenleri ---
    btnTaramaBaslat: TButton;
    RestRequestPOST: TRESTRequest;
    RestResponsePOST: TRESTResponse;

    // --- 3. Gün Bileşenleri (Gelişmiş Filtreler) ---
    cmbCalisanSayisi: TComboBox;
    edtMinPuan: TEdit;
    chkSadeceYatirimAlanlar: TCheckBox;

    procedure btnAraClick(Sender: TObject);
    procedure FormCreate(Sender: TObject);
    procedure btnTaramaBaslatClick(Sender: TObject);
  private
    { Private declarations }
    procedure GelismisAramaYap; // Eski APIyeBaglanVeAra'nın yerine bu geldi
  public
    { Public declarations }
  end;

var
  frmMain: TfrmMain;

implementation

{$R *.dfm}

procedure TfrmMain.FormCreate(Sender: TObject);
begin
  // Uygulama açıldığında varsayılan ayarlar
  edtSehir.TextHint := 'Şehir Giriniz (Örn: Ankara)';
  edtMinPuan.TextHint := 'Min Yapay Zeka Puanı (Örn: 85)';

  if cmbSektor.Items.Count = 0 then
    cmbSektor.Items.Add('Tümü');
  cmbSektor.ItemIndex := 0;

  if cmbCalisanSayisi.Items.Count = 0 then
    cmbCalisanSayisi.Items.Add('Tümü');
  cmbCalisanSayisi.ItemIndex := 0;
end;

// --- 3. GÜN: GET İSTEĞİ (QUERY BUILDER) ---
procedure TfrmMain.GelismisAramaYap;
begin
  RestRequest.Params.Clear;
  RestRequest.Method := rmGET;
  RestRequest.Resource := 'companies';

  if Trim(edtSehir.Text) <> '' then
    RestRequest.AddParameter('sehir', Trim(edtSehir.Text), pkGETrsUnsaved);

  if (cmbSektor.ItemIndex > -1) and (cmbSektor.Text <> 'Tümü') then
    RestRequest.AddParameter('sektor', cmbSektor.Text, pkGETrsUnsaved);

  if (cmbCalisanSayisi.ItemIndex > -1) and (cmbCalisanSayisi.Text <> 'Tümü') then
    RestRequest.AddParameter('calisan_araligi', cmbCalisanSayisi.Text, pkGETrsUnsaved);

  if Trim(edtMinPuan.Text) <> '' then
    RestRequest.AddParameter('min_puan', Trim(edtMinPuan.Text), pkGETrsUnsaved);

  if chkSadeceYatirimAlanlar.Checked then
    RestRequest.AddParameter('yatirim_aldi_mi', 'true', pkGETrsUnsaved);

  try
    RestRequest.Execute;
    if RestResponse.StatusCode = 200 then
    begin
      MemTableSonuclar.Close;
      MemTableSonuclar.Open;
    end
    else
      ShowMessage('Arama başarısız oldu. API Yanıt Kodu: ' + RestResponse.StatusCode.ToString);
  except
    on E: Exception do
      ShowMessage('API bağlantı hatası: ' + E.Message);
  end;
end;

procedure TfrmMain.btnAraClick(Sender: TObject);
begin
  GelismisAramaYap;
end;

// --- 2. GÜN: POST İSTEĞİ (ASENKRON TARAMA) ---
procedure TfrmMain.btnTaramaBaslatClick(Sender: TObject);
begin
  ShowMessage('OSINT Taraması arka planda başlatıldı. Lütfen bekleyin...');
  btnTaramaBaslat.Enabled := False;

  TTask.Run(procedure
  begin
    RestRequestPOST.Method := rmPOST;
    RestRequestPOST.Resource := 'companies/scan';

    try
      RestRequestPOST.Execute;
      TThread.Queue(nil, procedure
      begin
        if RestResponsePOST.StatusCode = 200 then
          ShowMessage('Tarama başarıyla tamamlandı!')
        else
          ShowMessage('Tarama hata kodu döndü: ' + RestResponsePOST.StatusCode.ToString);
        btnTaramaBaslat.Enabled := True;
      end);
    except
      on E: Exception do
      begin
        TThread.Queue(nil, procedure
        begin
          ShowMessage('API bağlantı hatası: ' + E.Message);
          btnTaramaBaslat.Enabled := True;
        end);
      end;
    end;
  end);
end;

end.